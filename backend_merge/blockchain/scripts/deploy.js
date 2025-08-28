const hre = require("hardhat");
const fs = require('fs');
const path = require('path');

async function main() {
  console.log("🚀 Deploying TrocServiceBafoka contract...");

  // Get the contract factory
  const TrocServiceBafoka = await hre.ethers.getContractFactory("TrocServiceBafoka");

  // Deploy the contract
  console.log("⏳ Deploying contract to network:", hre.network.name);
  
  const contract = await TrocServiceBafoka.deploy();
  await contract.waitForDeployment();

  const contractAddress = await contract.getAddress();
  console.log("✅ TrocServiceBafoka deployed to:", contractAddress);

  // Get the ABI
  const contractABI = TrocServiceBafoka.interface.formatJson();

  // Get deployer address
  const [deployer] = await hre.ethers.getSigners();
  const deployerAddress = await deployer.getAddress();
  
  // Save deployment info for Python backend
  const deploymentInfo = {
    address: contractAddress,
    abi: JSON.parse(contractABI),
    network: hre.network.name,
    deployer: deployerAddress,
    deploymentTime: new Date().toISOString(),
    blockNumber: await hre.ethers.provider.getBlockNumber()
  };

  // Create deployment directory if it doesn't exist
  const deploymentsDir = path.join(__dirname, '..', 'deployments');
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  // Save deployment info to JSON file
  const deploymentFile = path.join(deploymentsDir, `${hre.network.name}-deployment.json`);
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

  console.log("💾 Deployment info saved to:", deploymentFile);

  // Create Python contract configuration
  // Convert JavaScript JSON to Python-compatible format
  const pythonABI = JSON.stringify(deploymentInfo.abi, null, 4)
    .replace(/false/g, 'False')
    .replace(/true/g, 'True')
    .replace(/null/g, 'None');
  
  const pythonContractConfig = `# Auto-generated contract configuration
# Generated on: ${deploymentInfo.deploymentTime}

CONTRACT_ADDRESS = "${contractAddress}"
CONTRACT_ABI = ${pythonABI}

# Network Configuration
NETWORK_NAME = "${hre.network.name}"
DEPLOYER_ADDRESS = "${deploymentInfo.deployer}"
DEPLOYMENT_BLOCK = ${deploymentInfo.blockNumber}
`;

  // Save Python configuration
  const pythonConfigFile = path.join(__dirname, '..', 'Bafoka-teamZ-main', 'Bafoka-teamZ-back', 'backend_merge', 'contract_config.py');
  fs.writeFileSync(pythonConfigFile, pythonContractConfig);
  console.log("🐍 Python contract config saved to:", pythonConfigFile);

  // Print summary
  console.log("\n📄 Deployment Summary:");
  console.log("- Contract Address:", contractAddress);
  console.log("- Network:", hre.network.name);
  console.log("- Deployer:", deploymentInfo.deployer);
  console.log("- Block Number:", deploymentInfo.blockNumber);
  
  // Verify contract if on a public network
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("\n🔍 Waiting 30 seconds before verification...");
    await new Promise(resolve => setTimeout(resolve, 30000));
    
    try {
      await hre.run("verify:verify", {
        address: contractAddress,
        constructorArguments: [],
      });
      console.log("✅ Contract verified successfully!");
    } catch (error) {
      console.log("❌ Contract verification failed:", error.message);
    }
  }

  console.log("\n🎉 Deployment completed successfully!");
}

main().catch((error) => {
  console.error("❌ Deployment failed:", error);
  process.exitCode = 1;
});
