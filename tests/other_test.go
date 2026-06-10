// Tests in this file are run in the PR pipeline and the continuous testing pipeline
package test

import (
	"os"
	"os/exec"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/terraform-ibm-modules/ibmcloud-terratest-wrapper/testhelper"
)

// Use existing resource group
const resourceGroup = "geretain-test-resources"

// Ensure every example directory has a corresponding test
const landingZoneExampleDir = "containerized_app_landing_zone"
const hubAndSpokeSolutionDir = "hub-and-spoke"
const stacksDir = "stacks"

var IgnoreUpdates = []string{
	"module.logs_agent.helm_release.logs_agent",
	"module.logs_agent.terraform_data.install_required_binaries[0]",
}

var IgnoreDestroys = []string{
	"module.logs_agent.terraform_data.install_required_binaries[0]",
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

// Consistency test for the containerized app landing zone
func TestRunLandingZoneExample(t *testing.T) {
	t.Skip()
	t.Parallel()

	options := setupOptions(t, "app-lz", landingZoneExampleDir)

	output, err := options.RunTestConsistency()
	assert.Nil(t, err, "This should not have errored")
	assert.NotNil(t, output, "Expected some output")
}

// Consistency test for hub-and-spoke solution
func TestRunHubAndSpokeExample(t *testing.T) {
	t.Skip()
	t.Parallel()

	options := setupHubAndSpokeOptions(t)

	output, err := options.RunTestConsistency()
	assert.Nil(t, err, "This should not have errored")
	assert.NotNil(t, output, "Expected some output")
}

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
