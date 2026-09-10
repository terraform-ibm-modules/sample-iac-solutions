// Tests in this file are NOT run in the PR pipeline. They are run in the continuous testing pipeline along with the ones in pr_test.go
package test

import (
	"os"
	"os/exec"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
)

// Upgrade test for hub-and-spoke solution
func TestUpgradeRunHubAndSpokeExample(t *testing.T) {
	t.Skip()
	t.Parallel()

	options := setupHubAndSpokeOptions(t)
	output, err := options.RunTestUpgrade()
	if !options.UpgradeTestSkipped {
		assert.Nil(t, err, "This should not have errored")
		assert.NotNil(t, output, "Expected  some output")
	}
}

// Upgrade test for SecureInfraAIApp solution
func TestUpgradeSecureInfraAIAppExample(t *testing.T) {
	t.Parallel()
	options := setupSecureInfraAIAppOptions(t)
	output, err := options.RunTestUpgrade()
	if !options.UpgradeTestSkipped {
		assert.Nil(t, err, "This should not have errored")
		assert.NotNil(t, output, "Expected  some output")
	}
}

// Test for Terraform Stacks - validates stack configuration
// This test runs 'terraform stacks init' and 'terraform stacks validate'
// to validate the Terraform Stacks configuration.
//
// Note: The 'terraform stacks' commands require the Terraform stacks plugin which is available
// in the goldeneye-ci-image used in CI/CD pipelines. When running locally without the plugin,
// the test will be skipped.
func TestStacksValidation(t *testing.T) {
	t.Parallel()

	// Get the absolute path to the stacks directory
	stacksPath, err := filepath.Abs(filepath.Join("..", stacksDir))
	assert.Nil(t, err, "Failed to get absolute path to stacks directory")

	// Check if stacks directory exists
	if _, err := os.Stat(stacksPath); os.IsNotExist(err) {
		t.Skipf("Stacks directory not found at %s, skipping test", stacksPath)
		return
	}

	t.Logf("Testing Terraform Stack at: %s", stacksPath)

	// Check if terraform is installed
	terraformPath, err := exec.LookPath("terraform")
	if err != nil {
		t.Skip("Terraform CLI not found in PATH, skipping stack validation test")
		return
	}
	t.Logf("Using Terraform at: %s", terraformPath)

	// Check Terraform version
	versionCmd := exec.Command("terraform", "version", "-json")
	versionOutput, err := versionCmd.CombinedOutput()
	if err != nil {
		t.Logf("Warning: Could not check Terraform version: %v", err)
	} else {
		t.Logf("Terraform version info: %s", string(versionOutput))
	}

	// Check if terraform stacks command is available
	checkCmd := exec.Command("terraform", "stacks", "--help")
	_, checkErr := checkCmd.CombinedOutput()

	if checkErr != nil {
		// Stacks command not available - skip this test
		t.Skipf("Terraform stacks command not available (requires Terraform with stacks plugin). This test will run in CI with goldeneye-ci-image. Error: %v", checkErr)
		return
	}

	t.Log("✓ Terraform stacks command is available")

	listFilesCmd := exec.Command("find", ".", "-type", "f")
	listFilesCmd.Dir = stacksPath
	listFilesOutput, listFilesErr := listFilesCmd.CombinedOutput()
	if listFilesErr != nil {
		t.Logf("Warning: failed to list stack files: %v\nOutput: %s", listFilesErr, string(listFilesOutput))
	} else {
		t.Logf("Included stack files:\n%s", string(listFilesOutput))
	}

	// Step 1: Run terraform stacks init
	t.Log("Running terraform stacks init...")
	initCmd := exec.Command("terraform", "stacks", "init")
	initCmd.Dir = stacksPath
	initOutput, initErr := initCmd.CombinedOutput()

	t.Logf("Stacks init output:\n%s", string(initOutput))

	if initErr != nil {
		t.Fatalf("terraform stacks init failed: %v\nOutput: %s", initErr, string(initOutput))
	}

	t.Log("✓ terraform stacks init completed successfully")

	// Step 2: Run terraform stacks validate
	t.Log("Running terraform stacks validate...")
	validateCmd := exec.Command("terraform", "stacks", "validate")
	validateCmd.Dir = stacksPath
	validateOutput, validateErr := validateCmd.CombinedOutput()

	t.Logf("Stacks validate output:\n%s", string(validateOutput))

	if validateErr != nil {
		t.Fatalf("terraform stacks validate failed: %v\nOutput: %s", validateErr, string(validateOutput))
	}

	t.Log("✓ terraform stacks validate completed successfully")
	t.Log("✓ Stack configuration is valid and ready for deployment")
}
