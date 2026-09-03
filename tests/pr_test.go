// Tests in this file are run in the PR pipeline.
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
	"github.com/terraform-ibm-modules/ibmcloud-terratest-wrapper/common"
	"github.com/terraform-ibm-modules/ibmcloud-terratest-wrapper/testhelper"
)

// Use existing resource group
const resourceGroup = "geretain-test-resources"

// Ensure every example directory has a corresponding test
const landingZoneExampleDir = "containerized_app_landing_zone"
const hubAndSpokeSolutionDir = "hub-and-spoke"
const secureInfraAIAppDir = "secure-infra-ai-app"
const pulumiScriptDir = "pulumi/run_tests.sh"

var validRegions = []string{
	"au-syd",
	"ca-tor",
	"eu-de",
	"eu-gb",
	"jp-tok",
}

var IgnoreUpdates = []string{
	"module.logs_agent.helm_release.logs_agent",
	"module.logs_agent.terraform_data.install_required_binaries[0]",
	"module.monitoring_agent.helm_release.cloud_monitoring_agent",
	"module.monitoring_agent.terraform_data.install_required_binaries[0]",
}

var IgnoreDestroys = []string{
	"module.logs_agent.terraform_data.install_required_binaries[0]",
	"module.monitoring_agent.terraform_data.install_required_binaries[0]",
}

var IgnoreAdds = []string{
	"module.scc_wp.restapi_object.cspm",
	"module.app_config.ibm_config_aggregator_settings.config_aggregator_settings[0]",
}

func setupOptions(t *testing.T, prefix string, dir string) *testhelper.TestOptions {
	options := testhelper.TestOptionsDefaultWithVars(&testhelper.TestOptions{
		Testing:      t,
		TerraformDir: dir,
		Prefix:       prefix,
		Region:       "eu-de",
		IgnoreUpdates: testhelper.Exemptions{ // Ignore for consistency check
			List: IgnoreUpdates,
		},
		IgnoreDestroys: testhelper.Exemptions{ // Ignore destroy/recreate actions
			List: IgnoreDestroys,
		},
		IgnoreAdds: testhelper.Exemptions{
			List: IgnoreAdds,
		},
		TerraformVars: map[string]interface{}{
			"existing_resource_group_name": resourceGroup,
		},
	})
	return options
}

func setupHubAndSpokeOptions(t *testing.T) *testhelper.TestOptions {
	options := testhelper.TestOptionsDefault(&testhelper.TestOptions{
		Testing:      t,
		TerraformDir: hubAndSpokeSolutionDir,
		Prefix:       "hs",
		Region:       "us-south",
	})
	options.TerraformVars = map[string]interface{}{
		"prefix": options.Prefix,
		"region": options.Region,
	}
	return options
}

func setupSecureInfraAIAppOptions(t *testing.T) *testhelper.TestOptions {
	region := validRegions[common.CryptoIntn(len(validRegions))]
	options := testhelper.TestOptionsDefault(&testhelper.TestOptions{
		Testing:      t,
		TerraformDir: secureInfraAIAppDir,
		Prefix:       "sec-ai",
		Region:       region,
		IgnoreUpdates: testhelper.Exemptions{
			List: []string{
				"module.code_engine_app.ibm_code_engine_app.ce_app", // Added to resolve probe_liveness idempotency test failure —  Refer Issue - https://github.ibm.com/GoldenEye/issues/issues/17145
			},
		},
	})
	options.TerraformVars = map[string]interface{}{
		"prefix": options.Prefix,
		"region": options.Region,
	}
	return options
}

// Consistency test for the containerized app landing zone
func TestRunLandingZoneExample(t *testing.T) {
	t.Parallel()

	options := setupOptions(t, "app-lz", landingZoneExampleDir)

	output, err := options.RunTestConsistency()
	assert.Nil(t, err, "This should not have errored")
	assert.NotNil(t, output, "Expected some output")
}

// Upgrade test for the containerized app landing zone
func TestUpgradeLandingZoneExample(t *testing.T) {
	t.Parallel()

	options := setupOptions(t, "app-lz", landingZoneExampleDir)
	output, err := options.RunTestUpgrade()
	if !options.UpgradeTestSkipped {
		assert.Nil(t, err, "This should not have errored")
		assert.NotNil(t, output, "Expected  some output")
	}
}

// Consistency test for hub-and-spoke solution
func TestRunHubAndSpokeExample(t *testing.T) {
	t.Parallel()

	options := setupHubAndSpokeOptions(t)

	output, err := options.RunTestConsistency()
	assert.Nil(t, err, "This should not have errored")
	assert.NotNil(t, output, "Expected some output")
}

// Consistency test for the secure infra AI app
func TestRunSecureInfraAIAppExample(t *testing.T) {
	t.Parallel()

	options := setupSecureInfraAIAppOptions(t)

	output, err := options.RunTestConsistency()
	assert.Nil(t, err, "This should not have errored")
	assert.NotNil(t, output, "Expected some output")
}

// Test for Pulumi Python tests
func TestRunPulumiPythonTests(t *testing.T) {
	t.Parallel()

	// Execute the Python test script
	cmd := exec.Command("bash", pulumiScriptDir)
	output, err := cmd.CombinedOutput()

	// Print output for debugging
	t.Logf("Pulumi Python Test Output:\n%s", string(output))

	// Assert that the tests passed
	assert.Nil(t, err, "Pulumi Python tests should not have errored")
	assert.Contains(t, string(output), "passed", "Expected tests to pass")
	assert.NotContains(t, string(output), "FAILED", "Should not contain any failures")
}

// ############################################################################
// Terragrunt tests
// ############################################################################

const (
	terragruntDir  = "terragrunt"
	commandTimeout = 120 * time.Minute
)

// setupTerragruntOptions builds a TestOptions value pointing at the terragrunt
func setupTerragruntOptions(t *testing.T, prefix string) *testhelper.TestOptions {
	workingDir, err := os.Getwd()
	require.NoError(t, err, "Failed to get working directory")

	terragruntPath := filepath.Join(filepath.Dir(workingDir), terragruntDir)

	// Generate a short random numeric prefix for resource naming.
	const digits = "0123456789"
	raw := make([]byte, 4)
	for i := range raw {
		n, randErr := rand.Int(rand.Reader, big.NewInt(int64(len(digits))))
		if randErr != nil {
			panic(fmt.Sprintf("failed generating random prefix: %v", randErr))
		}
		raw[i] = digits[n.Int64()]
	}
	uniquePrefix := fmt.Sprintf("tg%s", string(raw))

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
	if _, err := exec.LookPath("terragrunt"); err != nil {
		t.Fatal("terragrunt executable not found in $PATH after setup — install terragrunt (https://terragrunt.gruntwork.io/docs/getting-started/install/) and ensure it is available before running this test")
	}
}

func runTerragruntCommand(t *testing.T, dir string, args ...string) (string, error) {
	// Ensure TG_TF_PATH points to the terraform binary if not already set.
	if os.Getenv("TG_TF_PATH") == "" {
		if terraformPath, err := exec.LookPath("terraform"); err == nil {
			_ = os.Setenv("TG_TF_PATH", terraformPath)
		}
	}

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

func cleanupTerragruntResources(t *testing.T, options *testhelper.TestOptions) {
	for _, module := range []string{"ocp", "vpc", "resource_group"} {
		modulePath := filepath.Join(options.TerraformDir, module)
		t.Logf("Cleaning up %s...", module)
		output, err := runTerragruntCommand(t, modulePath, "--non-interactive", "destroy", "--", "-auto-approve")
		if err != nil {
			t.Errorf("WARNING: Failed to destroy %s", module)
			t.Logf("Destroy output:\n%s", output)
			continue
		}
		t.Logf("Successfully destroyed %s", module)
	}
	t.Log("Cleanup completed")
}

func TestTerragruntDeployAll(t *testing.T) {
	skipIfNoAPIKey(t)
	setupTerragruntBinary(t)

	options := setupTerragruntOptions(t, "tg")

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
