// Tests in this file are NOT run in the PR pipeline. They are run in the continuous testing pipeline along with the ones in pr_test.go
package test

import (
	"github.com/stretchr/testify/assert"
	"testing"
)

// Consistency test for the containerized app landing zone
func TestRunLandingZoneExample(t *testing.T) {
	t.Parallel()

	options := setupOptions(t, "app-lz", landingZoneExampleDir)

	output, err := options.RunTestConsistency()
	assert.Nil(t, err, "This should not have errored")
	assert.NotNil(t, output, "Expected some output")
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
