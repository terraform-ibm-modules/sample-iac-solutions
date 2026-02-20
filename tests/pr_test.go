// Tests in this file are run in the PR pipeline and the continuous testing pipeline
package test

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/terraform-ibm-modules/ibmcloud-terratest-wrapper/testhelper"
)

// Use existing resource group
const resourceGroup = "geretain-test-resources"

// Ensure every example directory has a corresponding test
const landingZoneExampleDir = "containerized_app_landing_zone"

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

// Consistency test for the containerized app landing zone
func TestRunLandingZoneExample(t *testing.T) {
	t.Parallel()

	options := setupOptions(t, "app-lz", landingZoneExampleDir)

	output, err := options.RunTestConsistency()
	assert.Nil(t, err, "This should not have errored")
	assert.NotNil(t, output, "Expected some output")
}
