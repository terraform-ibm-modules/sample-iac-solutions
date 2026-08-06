package test

import (
	"bytes"
	"context"
	"crypto/rand"
	"encoding/json"
	"fmt"
	"io"
	"math/big"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/gruntwork-io/terratest/modules/logger"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/terraform-ibm-modules/ibmcloud-terratest-wrapper/testhelper"
)

const (
	terragruntDir  = "terragrunt"
	commandTimeout = 120 * time.Minute
)

func setupTerragruntOptions(t *testing.T, prefix string) *testhelper.TestOptions {
	workingDir, err := os.Getwd()
	require.NoError(t, err, "Failed to get working directory")

	terragruntPath := filepath.Join(filepath.Dir(workingDir), terragruntDir)

	uniquePrefix := generateUniquePrefix()

	t.Setenv("TG_PREFIX", uniquePrefix)

	clearTerragruntCache(t, terragruntPath)

	options := testhelper.TestOptionsDefault(&testhelper.TestOptions{
		Testing:      t,
		TerraformDir: terragruntPath,
		Prefix:       uniquePrefix,
		Region:       "eu-de",
	})

	options.TerraformVars = map[string]interface{}{}

	return options
}

func clearTerragruntCache(t *testing.T, terragruntPath string) {
	modules := []string{"resource_group", "vpc", "ocp"}
	for _, module := range modules {
		cachePath := filepath.Join(terragruntPath, module, ".terragrunt-cache")
		if err := os.RemoveAll(cachePath); err != nil {
			t.Logf("Warning: could not clear terragrunt cache at %s: %v", cachePath, err)
		} else {
			t.Logf("Cleared terragrunt cache for %s", module)
		}
	}
}

func skipIfNoAPIKey(t *testing.T) {
	if os.Getenv("TF_VAR_ibmcloud_api_key") == "" {
		t.Skip("Skipping test: IBM Cloud API key not set. Set TF_VAR_ibmcloud_api_key")
	}
}

func generateUniquePrefix() string {
	const digits = "0123456789"

	result := make([]byte, 4)
	for i := range result {
		n, err := rand.Int(rand.Reader, big.NewInt(int64(len(digits))))
		if err != nil {
			panic(fmt.Sprintf("failed generating random prefix: %v", err))
		}
		result[i] = digits[n.Int64()]
	}

	return fmt.Sprintf("tg%s", string(result))
}

func ensureTerraformPath() {
	if os.Getenv("TG_TF_PATH") != "" {
		return
	}

	terraformPath, err := exec.LookPath("terraform")
	if err == nil {
		_ = os.Setenv("TG_TF_PATH", terraformPath)
	}
}

func requireTerragruntInstalled(t *testing.T) {
	t.Helper()
	if _, err := exec.LookPath("terragrunt"); err != nil {
		t.Fatal("terragrunt executable not found in $PATH — install terragrunt (https://terragrunt.gruntwork.io/docs/getting-started/install/) and ensure it is available before running this test")
	}
}

// setupTerragruntBinary runs terraform init + apply on the terragrunt-setup module to
// install the terragrunt binary onto $PATH (/usr/local/bin) if not already present.
func setupTerragruntBinary(t *testing.T) {
	t.Helper()

	// Skip setup entirely if terragrunt is already on $PATH.
	if _, err := exec.LookPath("terragrunt"); err == nil {
		t.Log("terragrunt already on $PATH, skipping setup")
		return
	}

	workingDir, err := os.Getwd()
	require.NoError(t, err, "Failed to get working directory")

	setupDir := filepath.Join(workingDir, "terragrunt-setup")

	t.Log("Installing terragrunt via terragrunt-setup module...")

	setupOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: setupDir,
		Upgrade:      true,
		Logger:       logger.TestingT,
	})

	_, applyErr := terraform.InitAndApplyContextE(t, context.Background(), setupOptions)
	require.NoError(t, applyErr, "terragrunt-setup apply failed — could not install terragrunt")

	// Confirm the binary is now reachable on $PATH.
	requireTerragruntInstalled(t)
}

func runTerragruntCommand(t *testing.T, dir string, args ...string) (string, error) {
	ensureTerraformPath()

	ctx, cancel := context.WithTimeout(context.Background(), commandTimeout)
	defer cancel()

	t.Logf("Running: terragrunt %s (dir: %s)", strings.Join(args, " "), dir)

	cmd := exec.CommandContext(ctx, "terragrunt", args...)
	cmd.Dir = dir
	cmd.Env = os.Environ()

	var buf bytes.Buffer
	mw := io.MultiWriter(os.Stdout, &buf)
	cmd.Stdout = mw
	cmd.Stderr = mw

	err := cmd.Run()

	if ctx.Err() == context.DeadlineExceeded {
		return buf.String(), fmt.Errorf("command timed out after %s", commandTimeout)
	}

	if err != nil {
		return buf.String(), fmt.Errorf("command failed: %w", err)
	}

	return buf.String(), nil
}

func getTerragruntOutputs(t *testing.T, dir string) (map[string]interface{}, error) {

	output, err := runTerragruntCommand(t, dir, "--non-interactive", "--log-level", "error", "output", "-json", "-no-color")

	if err != nil {
		return nil, err
	}

	var outputs map[string]interface{}

	err = json.Unmarshal([]byte(output), &outputs)
	if err != nil {
		return nil, fmt.Errorf("failed parsing terragrunt output json: %w", err)
	}

	return outputs, nil
}

func assertOutputExists(t *testing.T, outputs map[string]interface{}, key string) {

	value, exists := outputs[key]

	assert.True(t, exists, "Expected output key %s to exist", key)
	assert.NotNil(t, value, "Expected output key %s to have non-nil value", key)
}

func cleanupModule(t *testing.T, modulePath string, moduleName string) {

	t.Logf("Cleaning up %s...", moduleName)

	output, err := runTerragruntCommand(t, modulePath, "--non-interactive", "destroy", "--", "-auto-approve")

	if err != nil {
		t.Errorf("WARNING: Failed to destroy %s", moduleName)
		t.Logf("Destroy output:\n%s", output)
		return
	}

	t.Logf("Successfully destroyed %s", moduleName)
}

func cleanupTerragruntResources(t *testing.T, options *testhelper.TestOptions) {

	modules := []string{
		"ocp",
		"vpc",
		"resource_group",
	}

	for _, module := range modules {
		modulePath := filepath.Join(options.TerraformDir, module)

		cleanupModule(t, modulePath, module)
	}

	t.Log("Cleanup completed")
}

func TestTerragruntDeployAll(t *testing.T) {
	skipIfNoAPIKey(t)
	setupTerragruntBinary(t)

	options := setupTerragruntOptions(t, "tg-test")

	defer func() {
		t.Log("Starting cleanup...")
		cleanupTerragruntResources(t, options)
		clearTerragruntCache(t, options.TerraformDir)
	}()

	t.Log("Running Terragrunt plan...")
	planOutput, err := runTerragruntCommand(t, options.TerraformDir, "--non-interactive", "run", "--all", "plan")
	require.NoError(t, err, "Terragrunt plan should not fail")
	assert.NotEmpty(t, planOutput)

	t.Log("Running Terragrunt apply...")
	applyOutput, err := runTerragruntCommand(t, options.TerraformDir, "--non-interactive", "run", "--all", "apply", "--", "-auto-approve")
	require.NoError(t, err, "Terragrunt apply should not fail")
	assert.NotEmpty(t, applyOutput)

	verifyResourceGroupOutputs(t, options)
	verifyVPCOutputs(t, options)
	verifyOCPOutputs(t, options)

	t.Log("Running plan again to verify idempotency...")
	idempotencyOutput, err := runTerragruntCommand(t, options.TerraformDir, "--non-interactive", "run", "--all", "plan")
	require.NoError(t, err, "Idempotency plan should not fail")
	noChanges := strings.Contains(idempotencyOutput, "No changes") || strings.Contains(idempotencyOutput, "0 added, 0 changed, 0 destroyed")
	assert.True(t, noChanges, "Infrastructure should have no changes after apply")

	t.Log("TestTerragruntDeployAll completed successfully")
}

func verifyResourceGroupOutputs(t *testing.T, options *testhelper.TestOptions) {

	rgPath := options.TerraformDir

	if !strings.HasSuffix(rgPath, "resource_group") {
		rgPath = filepath.Join(options.TerraformDir, "resource_group")
	}

	outputs, err := getTerragruntOutputs(t, rgPath)
	require.NoError(t, err)
	assertOutputExists(t, outputs, "resource_group_id")

	t.Log("Resource group outputs verified")
}

func verifyVPCOutputs(t *testing.T, options *testhelper.TestOptions) {

	vpcPath := options.TerraformDir

	if !strings.HasSuffix(vpcPath, "vpc") {
		vpcPath = filepath.Join(options.TerraformDir, "vpc")
	}

	outputs, err := getTerragruntOutputs(t, vpcPath)
	require.NoError(t, err)
	assertOutputExists(t, outputs, "vpc_id")
	assertOutputExists(t, outputs, "subnet_detail_map")
	t.Log("VPC outputs verified")
}

func verifyOCPOutputs(t *testing.T, options *testhelper.TestOptions) {

	ocpPath := filepath.Join(options.TerraformDir, "ocp")

	outputs, err := getTerragruntOutputs(t, ocpPath)
	require.NoError(t, err)
	assertOutputExists(t, outputs, "cluster_id")

	t.Log("OCP outputs verified")
}
