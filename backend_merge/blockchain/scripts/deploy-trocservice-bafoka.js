const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Deploying TrocService Bafoka - Unified Community Service Exchange Contract...");
  
  // Get the contract factory
  const TrocServiceBafoka = await ethers.getContractFactory("TrocServiceBafoka");
  
  // Deploy the contract
  const trocServiceContract = await TrocServiceBafoka.deploy();
  
  // Wait for deployment to finish
  await trocServiceContract.waitForDeployment();
  
  // Get contract address for reuse
  const contractAddress = await trocServiceContract.getAddress();
  
  console.log("✅ TrocService Bafoka deployed successfully!");
  console.log("📍 Contract Address:", contractAddress);
  console.log("🌐 Network:", network.name);
  
  // Verify the deployment
  console.log("\n🔍 Verifying contract deployment...");
  
  try {
    // Wait a bit for the deployment to be indexed
    console.log("⏳ Waiting for deployment to be indexed...");
    await new Promise(resolve => setTimeout(resolve, 30000));
    
    // Verify on Etherscan (if on a public network)
    if (network.name !== "hardhat" && network.name !== "localhost") {
      console.log("🔍 Verifying on Etherscan...");
      await hre.run("verify:verify", {
        address: contractAddress,
        constructorArguments: [],
      });
      console.log("✅ Contract verified on Etherscan!");
    }
  } catch (error) {
    console.log("⚠️  Verification failed:", error.message);
  }
  
  // Display initial community information
  console.log("\n🏘️  Initial Communities Created:");
  console.log("1. Fondjomenkwet (Fonjoka)");
  console.log("2. Banja (Banjika)");
  console.log("3. Bafouka (Bafouka)");
  
  console.log("\n💰 Initial Bafoka Distribution: 1000 per user");
  console.log("🔒 Community Isolation: Exchanges only within same community");
  console.log("🏪 Backer System: Local businesses can recharge accounts");
  console.log("⭐ Reputation System: Decentralized trust management");
  console.log("📱 Service Offers: Create and manage service listings");
  
  // Save deployment info
  const deploymentInfo = {
    contractName: "TrocServiceBafoka",
    address: contractAddress,
    network: network.name,
    deployer: (await ethers.getSigners())[0].address,
    deploymentTime: new Date().toISOString(),
    features: [
      "Unified community service exchange platform",
      "Local currency variants (Fonjoka, Banjika, Bafouka)",
      "Automatic 1000 Bafoka distribution",
      "Community isolation and membership management",
      "Service offer creation and management",
      "Smart contract escrow for exchanges",
      "Decentralized reputation system",
      "Backer recharge system with commission",
      "Comprehensive statistics and analytics",
      "Admin controls and emergency functions"
    ],
    contractSize: "~15KB (optimized)",
    gasOptimized: true,
    securityFeatures: [
      "ReentrancyGuard protection",
      "Ownable access control",
      "Input validation",
      "State management",
      "Event logging"
    ]
  };
  
  console.log("\n📋 Deployment Summary:");
  console.log(JSON.stringify(deploymentInfo, null, 2));
  
  console.log("\n🎉 Deployment Complete! Your unified TrocService Bafoka contract is ready!");
  console.log("\n📱 Next Steps:");
  console.log("1. Update your WhatsApp bot to use this unified contract");
  console.log("2. Test all functionality: registration, offers, exchanges, backers");
  console.log("3. Verify community isolation and currency management");
  console.log("4. Test reputation system and statistics");
  console.log("5. Deploy to production with monitoring");
  
  console.log("\n🔗 Contract Links:");
  if (network.name === "sepolia") {
    console.log(`Etherscan: https://sepolia.etherscan.io/address/${contractAddress}`);
  } else if (network.name === "mumbai") {
    console.log(`Polygonscan: https://mumbai.polygonscan.com/address/${contractAddress}`);
  } else if (network.name === "polygon") {
    console.log(`Polygonscan: https://polygonscan.com/address/${contractAddress}`);
  }
  
  console.log("\n📚 Documentation:");
  console.log("- README.md: Project overview and setup");
  console.log("- BAFOKA-COMMUNITY-DEPLOYMENT.md: Deployment guide");
  console.log("- whatsapp-conversation-script.md: WhatsApp integration");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
