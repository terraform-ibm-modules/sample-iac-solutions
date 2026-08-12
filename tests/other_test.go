// Tests in this file are NOT run in the PR pipeline. They are run in the continuous testing pipeline along with the ones in pr_test.go
package test

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// Upgrade test for hub-and-spoke solution
func TestUpgradeRunHubAndSpokeExample(t *testing.T) {
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
