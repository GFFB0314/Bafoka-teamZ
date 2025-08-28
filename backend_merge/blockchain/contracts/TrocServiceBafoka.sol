// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title TrocServiceBafoka - Unified Community Service Exchange Contract
 * @dev Complete marketplace for community-based service exchanges using local digital currency
 * Combines community management, service exchanges, reputation system, and backer functionality
 */
contract TrocServiceBafoka is ERC20, Ownable, ReentrancyGuard {
    
    // ========== STRUCTURES ==========
    
    struct Community {
        string name;
        string currencyName;
        uint256 communityId;
        bool exists;
        uint256 totalMembers;
        uint256 totalTransactions;
        uint256 totalVolume;
    }
    
    struct UserProfile {
        uint256 communityId;
        string username;
        bool isRegistered;
        uint256 reputation;
        uint256 totalExchanges;
        uint256 joinDate;
        bool isBacker;
        uint256 totalEarned;
        uint256 totalSpent;
    }
    
    struct ServiceOffer {
        uint256 offerId;
        address provider;
        string serviceDescription;
        uint256 price;
        uint256 communityId;
        bool isActive;
        uint256 createdAt;
        uint256 expiresAt;
        uint256 totalOrders;
        uint256 averageRating;
    }
    
    struct ExchangeAgreement {
        uint256 exchangeId;
        address provider;
        address receiver;
        uint256 communityId;
        string serviceDescription;
        uint256 bafokaAmount;
        uint256 deadline;
        bool isConfirmed;
        bool isCompleted;
        bool isFinalized;
        uint256 providerRating;
        uint256 receiverRating;
        uint256 createdAt;
        string status; // "pending", "confirmed", "completed", "finalized", "cancelled"
    }
    
    struct Backer {
        address backerAddress;
        uint256 communityId;
        string businessName;
        bool isActive;
        uint256 totalRecharges;
        uint256 totalVolume;
        uint256 commissionRate;
        uint256 lastRechargeDate;
    }
    
    struct ReputationHistory {
        uint256 exchangeId;
        uint256 rating;
        string comment;
        uint256 timestamp;
        address from;
    }
    
    // ========== STATE VARIABLES ==========
    
    mapping(uint256 => Community) public communities;
    mapping(address => UserProfile) public userProfiles;
    mapping(uint256 => ServiceOffer) public serviceOffers;
    mapping(uint256 => ExchangeAgreement) public exchangeAgreements;
    mapping(address => Backer) public backers;
    mapping(uint256 => mapping(address => uint256)) public communityBalances;
    mapping(address => ReputationHistory[]) public reputationHistory;
    mapping(uint256 => mapping(address => bool)) public communityMembership;
    
    // Counters
    uint256 public nextCommunityId;
    uint256 public nextOfferId;
    uint256 public nextExchangeId;
    uint256 public totalUsers;
    uint256 public totalVolume;
    
    // Constants
    uint256 public constant INITIAL_BAFOKA = 1000;
    uint256 public constant MIN_REPUTATION = 0;
    uint256 public constant MAX_REPUTATION = 100;
    uint256 public constant MIN_SERVICE_PRICE = 10;
    uint256 public constant MAX_SERVICE_PRICE = 10000;
    uint256 public constant OFFER_EXPIRY_DAYS = 30;
    uint256 public constant BACKER_COMMISSION_RATE = 5; // 5%
    
    // Events
    event CommunityCreated(uint256 indexed communityId, string name, string currencyName);
    event UserRegistered(address indexed user, uint256 indexed communityId, string username);
    event BafokaDistributed(address indexed user, uint256 indexed communityId, uint256 amount);
    event ServiceOfferCreated(uint256 indexed offerId, address indexed provider, string description, uint256 price);
    event ServiceOfferUpdated(uint256 indexed offerId, string description, uint256 price);
    event ServiceOfferDeactivated(uint256 indexed offerId);
    event ExchangeCreated(uint256 indexed exchangeId, address indexed provider, address indexed receiver, uint256 communityId);
    event ExchangeConfirmed(uint256 indexed exchangeId);
    event ExchangeCompleted(uint256 indexed exchangeId);
    event ExchangeFinalized(uint256 indexed exchangeId, uint256 providerRating, uint256 receiverRating);
    event ExchangeCancelled(uint256 indexed exchangeId, address indexed cancelledBy);
    event BackerRegistered(address indexed backer, uint256 indexed communityId, string businessName);
    event BafokaRecharged(address indexed user, address indexed backer, uint256 indexed communityId, uint256 amount, uint256 commission);
    event ReputationUpdated(address indexed user, uint256 indexed exchangeId, uint256 rating, string comment);
    event CommunityStatsUpdated(uint256 indexed communityId, uint256 totalMembers, uint256 totalTransactions, uint256 totalVolume);
    
    // ========== CONSTRUCTOR ==========
    
    constructor() ERC20("TrocService Bafoka", "TSB") Ownable(msg.sender) {
        nextCommunityId = 1;
        nextOfferId = 1;
        nextExchangeId = 1;
        
        // Create initial communities
        _createCommunity("Fondjomenkwet", "Fonjoka");
        _createCommunity("Banja", "Banjika");
        _createCommunity("Bafouka", "Bafouka");
    }
    
    // ========== COMMUNITY MANAGEMENT ==========
    
    /**
     * @dev Create a new community
     * @param name Community name
     * @param currencyName Local currency name (e.g., "Fonjoka")
     */
    function _createCommunity(string memory name, string memory currencyName) private {
        communities[nextCommunityId] = Community({
            name: name,
            currencyName: currencyName,
            communityId: nextCommunityId,
            exists: true,
            totalMembers: 0,
            totalTransactions: 0,
            totalVolume: 0
        });
        
        emit CommunityCreated(nextCommunityId, name, currencyName);
        nextCommunityId++;
    }
    
    /**
     * @dev Add a new community (only owner)
     * @param name Community name
     * @param currencyName Local currency name
     */
    function addCommunity(string memory name, string memory currencyName) external onlyOwner {
        require(bytes(name).length > 0, "Community name cannot be empty");
        require(bytes(currencyName).length > 0, "Currency name cannot be empty");
        
        communities[nextCommunityId] = Community({
            name: name,
            currencyName: currencyName,
            communityId: nextCommunityId,
            exists: true,
            totalMembers: 0,
            totalTransactions: 0,
            totalVolume: 0
        });
        
        emit CommunityCreated(nextCommunityId, name, currencyName);
        nextCommunityId++;
    }
    
    // ========== USER REGISTRATION ==========
    
    /**
     * @dev Register a new user in a specific community
     * @param communityId The community ID to join
     * @param username User's display name
     */
    function registerUser(uint256 communityId, string memory username) external {
        require(communities[communityId].exists, "Community does not exist");
        require(!userProfiles[msg.sender].isRegistered, "User already registered");
        require(bytes(username).length > 0, "Username cannot be empty");
        require(bytes(username).length <= 50, "Username too long");
        
        // Create user profile
        userProfiles[msg.sender] = UserProfile({
            communityId: communityId,
            username: username,
            isRegistered: true,
            reputation: 50, // Start with neutral reputation
            totalExchanges: 0,
            joinDate: block.timestamp,
            isBacker: false,
            totalEarned: 0,
            totalSpent: 0
        });
        
        // Distribute initial Bafoka
        communityBalances[communityId][msg.sender] = INITIAL_BAFOKA;
        communityMembership[communityId][msg.sender] = true;
        
        // Update counters
        communities[communityId].totalMembers++;
        totalUsers++;
        
        emit UserRegistered(msg.sender, communityId, username);
        emit BafokaDistributed(msg.sender, communityId, INITIAL_BAFOKA);
    }
    
    // ========== SERVICE OFFERS ==========
    
    /**
     * @dev Create a new service offer
     * @param serviceDescription Description of the service
     * @param price Price in Bafoka
     * @param expiryDays Days until offer expires
     */
    function createServiceOffer(
        string memory serviceDescription,
        uint256 price,
        uint256 expiryDays
    ) external returns (uint256) {
        require(userProfiles[msg.sender].isRegistered, "User not registered");
        require(bytes(serviceDescription).length > 0, "Service description cannot be empty");
        require(bytes(serviceDescription).length <= 500, "Service description too long");
        require(price >= MIN_SERVICE_PRICE, "Price too low");
        require(price <= MAX_SERVICE_PRICE, "Price too high");
        require(expiryDays > 0 && expiryDays <= 365, "Invalid expiry days");
        
        uint256 communityId = userProfiles[msg.sender].communityId;
        uint256 expiryTime = block.timestamp + (expiryDays * 1 days);
        
        serviceOffers[nextOfferId] = ServiceOffer({
            offerId: nextOfferId,
            provider: msg.sender,
            serviceDescription: serviceDescription,
            price: price,
            communityId: communityId,
            isActive: true,
            createdAt: block.timestamp,
            expiresAt: expiryTime,
            totalOrders: 0,
            averageRating: 0
        });
        
        emit ServiceOfferCreated(nextOfferId, msg.sender, serviceDescription, price);
        
        return nextOfferId++;
    }
    
    /**
     * @dev Update an existing service offer
     * @param offerId The offer ID to update
     * @param serviceDescription New description
     * @param price New price
     */
    function updateServiceOffer(
        uint256 offerId,
        string memory serviceDescription,
        uint256 price
    ) external {
        ServiceOffer storage offer = serviceOffers[offerId];
        require(offer.provider == msg.sender, "Not the offer owner");
        require(offer.isActive, "Offer not active");
        require(block.timestamp < offer.expiresAt, "Offer expired");
        require(bytes(serviceDescription).length > 0, "Service description cannot be empty");
        require(price >= MIN_SERVICE_PRICE, "Price too low");
        require(price <= MAX_SERVICE_PRICE, "Price too high");
        
        offer.serviceDescription = serviceDescription;
        offer.price = price;
        
        emit ServiceOfferUpdated(offerId, serviceDescription, price);
    }
    
    /**
     * @dev Deactivate a service offer
     * @param offerId The offer ID to deactivate
     */
    function deactivateServiceOffer(uint256 offerId) external {
        ServiceOffer storage offer = serviceOffers[offerId];
        require(offer.provider == msg.sender, "Not the offer owner");
        require(offer.isActive, "Offer already inactive");
        
        offer.isActive = false;
        
        emit ServiceOfferDeactivated(offerId);
    }
    
    // ========== EXCHANGE MANAGEMENT ==========
    
    /**
     * @dev Create a new exchange agreement
     * @param receiver Service receiver address
     * @param serviceDescription Description of the service
     * @param bafokaAmount Amount of Bafoka for the service
     * @param deadline Deadline for completion
     */
    function createExchange(
        address receiver,
        string memory serviceDescription,
        uint256 bafokaAmount,
        uint256 deadline
    ) external returns (uint256) {
        require(userProfiles[msg.sender].isRegistered, "Provider not registered");
        require(userProfiles[receiver].isRegistered, "Receiver not registered");
        require(msg.sender != receiver, "Cannot exchange with yourself");
        
        uint256 communityId = userProfiles[msg.sender].communityId;
        require(userProfiles[receiver].communityId == communityId, "Users must be in same community");
        require(communityBalances[communityId][msg.sender] >= bafokaAmount, "Insufficient Bafoka");
        require(deadline > block.timestamp, "Deadline must be in the future");
        require(deadline <= block.timestamp + 365 days, "Deadline too far in future");
        require(bafokaAmount > 0, "Amount must be greater than 0");
        
        // Create exchange agreement
        exchangeAgreements[nextExchangeId] = ExchangeAgreement({
            exchangeId: nextExchangeId,
            provider: msg.sender,
            receiver: receiver,
            communityId: communityId,
            serviceDescription: serviceDescription,
            bafokaAmount: bafokaAmount,
            deadline: deadline,
            isConfirmed: false,
            isCompleted: false,
            isFinalized: false,
            providerRating: 0,
            receiverRating: 0,
            createdAt: block.timestamp,
            status: "pending"
        });
        
        // Reserve Bafoka
        communityBalances[communityId][msg.sender] -= bafokaAmount;
        
        emit ExchangeCreated(nextExchangeId, msg.sender, receiver, communityId);
        
        return nextExchangeId++;
    }
    
    /**
     * @dev Confirm an exchange agreement
     * @param exchangeId The exchange ID to confirm
     */
    function confirmExchange(uint256 exchangeId) external {
        ExchangeAgreement storage agreement = exchangeAgreements[exchangeId];
        require(agreement.receiver == msg.sender, "Only receiver can confirm");
        require(!agreement.isConfirmed, "Exchange already confirmed");
        require(!agreement.isCompleted, "Exchange already completed");
        require(block.timestamp <= agreement.deadline, "Exchange deadline passed");
        require(keccak256(bytes(agreement.status)) == keccak256(bytes("pending")), "Invalid status");
        
        agreement.isConfirmed = true;
        agreement.status = "confirmed";
        
        emit ExchangeConfirmed(exchangeId);
    }
    
    /**
     * @dev Mark an exchange as completed
     * @param exchangeId The exchange ID to mark as completed
     */
    function markExchangeCompleted(uint256 exchangeId) external {
        ExchangeAgreement storage agreement = exchangeAgreements[exchangeId];
        require(agreement.isConfirmed, "Exchange not confirmed");
        require(!agreement.isCompleted, "Exchange already completed");
        require(msg.sender == agreement.provider || msg.sender == agreement.receiver, "Not authorized");
        require(keccak256(bytes(agreement.status)) == keccak256(bytes("confirmed")), "Invalid status");
        
        agreement.isCompleted = true;
        agreement.status = "completed";
        
        emit ExchangeCompleted(exchangeId);
    }
    
    /**
     * @dev Cancel an exchange (only before confirmation)
     * @param exchangeId The exchange ID to cancel
     */
    function cancelExchange(uint256 exchangeId) external {
        ExchangeAgreement storage agreement = exchangeAgreements[exchangeId];
        require(msg.sender == agreement.provider || msg.sender == agreement.receiver, "Not authorized");
        require(!agreement.isConfirmed, "Cannot cancel confirmed exchange");
        require(keccak256(bytes(agreement.status)) == keccak256(bytes("pending")), "Invalid status");
        
        agreement.status = "cancelled";
        
        // Refund Bafoka to provider
        if (msg.sender == agreement.provider) {
            communityBalances[agreement.communityId][agreement.provider] += agreement.bafokaAmount;
        }
        
        emit ExchangeCancelled(exchangeId, msg.sender);
    }
    
    /**
     * @dev Finalize an exchange with ratings
     * @param exchangeId The exchange ID to finalize
     * @param providerRating Rating for the provider (1-5)
     * @param receiverRating Rating for the receiver (1-5)
     * @param comment Comment about the exchange
     */
    function finalizeExchange(
        uint256 exchangeId,
        uint256 providerRating,
        uint256 receiverRating,
        string memory comment
    ) external nonReentrant {
        ExchangeAgreement storage agreement = exchangeAgreements[exchangeId];
        require(agreement.isCompleted, "Exchange not completed");
        require(!agreement.isFinalized, "Exchange already finalized");
        require(msg.sender == agreement.provider || msg.sender == agreement.receiver, "Not authorized");
        require(providerRating >= 1 && providerRating <= 5, "Invalid provider rating");
        require(receiverRating >= 1 && receiverRating <= 5, "Invalid receiver rating");
        require(keccak256(bytes(agreement.status)) == keccak256(bytes("completed")), "Invalid status");
        
        // Transfer Bafoka to provider
        communityBalances[agreement.communityId][agreement.provider] += agreement.bafokaAmount;
        
        // Update ratings and reputation
        agreement.providerRating = providerRating;
        agreement.receiverRating = receiverRating;
        agreement.isFinalized = true;
        agreement.status = "finalized";
        
        // Update user statistics
        userProfiles[agreement.provider].totalExchanges++;
        userProfiles[agreement.provider].totalEarned += agreement.bafokaAmount;
        userProfiles[agreement.receiver].totalExchanges++;
        userProfiles[agreement.receiver].totalSpent += agreement.bafokaAmount;
        
        // Update reputation
        _updateReputation(agreement.provider, providerRating, exchangeId, comment);
        _updateReputation(agreement.receiver, receiverRating, exchangeId, comment);
        
        // Update community statistics
        communities[agreement.communityId].totalTransactions++;
        communities[agreement.communityId].totalVolume += agreement.bafokaAmount;
        totalVolume += agreement.bafokaAmount;
        
        emit ExchangeFinalized(exchangeId, providerRating, receiverRating);
        emit CommunityStatsUpdated(agreement.communityId, communities[agreement.communityId].totalMembers, communities[agreement.communityId].totalTransactions, communities[agreement.communityId].totalVolume);
    }
    
    // ========== REPUTATION SYSTEM ==========
    
    /**
     * @dev Update user reputation based on rating
     * @param user User address
     * @param rating Rating received (1-5)
     * @param exchangeId Exchange ID
     * @param comment Comment about the exchange
     */
    function _updateReputation(
        address user,
        uint256 rating,
        uint256 exchangeId,
        string memory comment
    ) private {
        UserProfile storage profile = userProfiles[user];
        
        // Store reputation history
        reputationHistory[user].push(ReputationHistory({
            exchangeId: exchangeId,
            rating: rating,
            comment: comment,
            timestamp: block.timestamp,
            from: msg.sender
        }));
        
        // Update reputation score (weighted average)
        if (rating >= 4) {
            profile.reputation = profile.reputation < MAX_REPUTATION ? profile.reputation + 1 : MAX_REPUTATION;
        } else if (rating <= 2) {
            profile.reputation = profile.reputation > MIN_REPUTATION ? profile.reputation - 1 : MIN_REPUTATION;
        }
        
        emit ReputationUpdated(user, exchangeId, rating, comment);
    }
    
    // ========== BACKER SYSTEM ==========
    
    /**
     * @dev Register a backer for a community
     * @param communityId The community ID
     * @param businessName Name of the business
     */
    function registerBacker(uint256 communityId, string memory businessName) external {
        require(communities[communityId].exists, "Community does not exist");
        require(userProfiles[msg.sender].isRegistered, "User not registered");
        require(userProfiles[msg.sender].communityId == communityId, "User not in this community");
        require(bytes(businessName).length > 0, "Business name cannot be empty");
        require(bytes(businessName).length <= 100, "Business name too long");
        
        backers[msg.sender] = Backer({
            backerAddress: msg.sender,
            communityId: communityId,
            businessName: businessName,
            isActive: true,
            totalRecharges: 0,
            totalVolume: 0,
            commissionRate: BACKER_COMMISSION_RATE,
            lastRechargeDate: block.timestamp
        });
        
        userProfiles[msg.sender].isBacker = true;
        
        emit BackerRegistered(msg.sender, communityId, businessName);
    }
    
    /**
     * @dev Recharge user's Bafoka account (only backers can do this)
     * @param user User to recharge
     * @param amount Amount of Bafoka to add
     */
    function rechargeBafoka(address user, uint256 amount) external {
        require(backers[msg.sender].isActive, "Not an active backer");
        require(userProfiles[user].isRegistered, "User not registered");
        require(backers[msg.sender].communityId == userProfiles[user].communityId, "Different communities");
        require(amount > 0, "Amount must be greater than 0");
        require(amount <= 10000, "Amount too high");
        
        uint256 communityId = backers[msg.sender].communityId;
        uint256 commission = (amount * backers[msg.sender].commissionRate) / 100;
        uint256 netAmount = amount - commission;
        
        // Add Bafoka to user's account
        communityBalances[communityId][user] += netAmount;
        
        // Update backer statistics
        backers[msg.sender].totalRecharges++;
        backers[msg.sender].totalVolume += amount;
        backers[msg.sender].lastRechargeDate = block.timestamp;
        
        emit BafokaRecharged(user, msg.sender, communityId, netAmount, commission);
    }
    
    // ========== VIEW FUNCTIONS ==========
    
    /**
     * @dev Get user's Bafoka balance for a specific community
     * @param user User address
     * @param communityId Community ID
     * @return Balance amount
     */
    function getCommunityBalance(address user, uint256 communityId) external view returns (uint256) {
        return communityBalances[communityId][user];
    }
    
    /**
     * @dev Get user profile information
     * @param user User address
     * @return Profile information
     */
    function getUserProfile(address user) external view returns (UserProfile memory) {
        return userProfiles[user];
    }
    
    /**
     * @dev Get community information
     * @param communityId Community ID
     * @return Community information
     */
    function getCommunity(uint256 communityId) external view returns (Community memory) {
        return communities[communityId];
    }
    
    /**
     * @dev Get service offer details
     * @param offerId Offer ID
     * @return Service offer details
     */
    function getServiceOffer(uint256 offerId) external view returns (ServiceOffer memory) {
        return serviceOffers[offerId];
    }
    
    /**
     * @dev Get exchange agreement details
     * @param exchangeId Exchange ID
     * @return Exchange agreement details
     */
    function getExchangeAgreement(uint256 exchangeId) external view returns (ExchangeAgreement memory) {
        return exchangeAgreements[exchangeId];
    }
    
    /**
     * @dev Get backer information
     * @param backer Backer address
     * @return Backer information
     */
    function getBacker(address backer) external view returns (Backer memory) {
        return backers[backer];
    }
    
    /**
     * @dev Get user's reputation history
     * @param user User address
     * @return Array of reputation history entries
     */
    function getUserReputationHistory(address user) external view returns (ReputationHistory[] memory) {
        return reputationHistory[user];
    }
    
    /**
     * @dev Get active service offers for a community
     * @param communityId Community ID
     * @param limit Maximum number of offers to return
     * @return Array of active service offers
     */
    function getActiveServiceOffers(uint256 communityId, uint256 limit) external view returns (ServiceOffer[] memory) {
        uint256 activeCount = 0;
        uint256[] memory activeIds = new uint256[](limit);
        
        // Count active offers
        for (uint256 i = 1; i < nextOfferId; i++) {
            if (serviceOffers[i].isActive && 
                serviceOffers[i].communityId == communityId && 
                serviceOffers[i].expiresAt > block.timestamp) {
                activeIds[activeCount] = i;
                activeCount++;
                if (activeCount >= limit) break;
            }
        }
        
        // Create result array
        ServiceOffer[] memory result = new ServiceOffer[](activeCount);
        for (uint256 i = 0; i < activeCount; i++) {
            result[i] = serviceOffers[activeIds[i]];
        }
        
        return result;
    }
    
    /**
     * @dev Get user's active exchanges
     * @param user User address
     * @return Array of active exchanges
     */
    function getUserActiveExchanges(address user) external view returns (ExchangeAgreement[] memory) {
        uint256 activeCount = 0;
        uint256[] memory activeIds = new uint256[](nextExchangeId);
        
        // Count active exchanges
        for (uint256 i = 1; i < nextExchangeId; i++) {
            if ((exchangeAgreements[i].provider == user || exchangeAgreements[i].receiver == user) &&
                !exchangeAgreements[i].isFinalized && 
                keccak256(bytes(exchangeAgreements[i].status)) != keccak256(bytes("cancelled"))) {
                activeIds[activeCount] = i;
                activeCount++;
            }
        }
        
        // Create result array
        ExchangeAgreement[] memory result = new ExchangeAgreement[](activeCount);
        for (uint256 i = 0; i < activeCount; i++) {
            result[i] = exchangeAgreements[activeIds[i]];
        }
        
        return result;
    }
    
    // ========== ADMIN FUNCTIONS ==========
    
    /**
     * @dev Update backer commission rate (only owner)
     * @param backer Backer address
     * @param newRate New commission rate (percentage)
     */
    function updateBackerCommissionRate(address backer, uint256 newRate) external onlyOwner {
        require(backers[backer].isActive, "Backer not active");
        require(newRate >= 1 && newRate <= 20, "Invalid commission rate");
        
        backers[backer].commissionRate = newRate;
    }
    
    /**
     * @dev Deactivate a backer (only owner)
     * @param backer Backer address
     */
    function deactivateBacker(address backer) external onlyOwner {
        require(backers[backer].isActive, "Backer already inactive");
        
        backers[backer].isActive = false;
        userProfiles[backer].isBacker = false;
    }
    
    /**
     * @dev Emergency pause all exchanges (only owner)
     */
    function emergencyPause() external onlyOwner {
        // This would pause all critical functions
        // Implementation depends on specific requirements
    }
    
    // ========== UTILITY FUNCTIONS ==========
    
    /**
     * @dev Check if user is member of a community
     * @param user User address
     * @param communityId Community ID
     * @return True if user is member
     */
    function isCommunityMember(address user, uint256 communityId) external view returns (bool) {
        return communityMembership[communityId][user];
    }
    
    /**
     * @dev Get total statistics
     * @return Total users, total volume, total communities
     */
    function getTotalStats() external view returns (uint256, uint256, uint256) {
        return (totalUsers, totalVolume, nextCommunityId - 1);
    }
    
    /**
     * @dev Get community statistics
     * @param communityId Community ID
     * @return Member count, transaction count, total volume
     */
    function getCommunityStats(uint256 communityId) external view returns (uint256, uint256, uint256) {
        Community storage community = communities[communityId];
        return (community.totalMembers, community.totalTransactions, community.totalVolume);
    }
}
