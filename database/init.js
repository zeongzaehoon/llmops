// MongoDB initialization script
// Runs on first container startup (when /data/db is empty)

const dbName = process.env.MONGO_INITDB_DATABASE || "solomon";
const rootUser = process.env.MONGO_INITDB_ROOT_USERNAME;
const rootPassword = process.env.MONGO_INITDB_ROOT_PASSWORD;

db = db.getSiblingDB(dbName);

// Create application user with readWrite permissions
db.createUser({
  user: rootUser,
  pwd: rootPassword,
  roles: [
    { role: "readWrite", db: dbName },
  ],
});

// Pre-create collections used by the API
const collections = [
  "solomonChatHistory",
  "solomonPromptHistory",
  "solomonModels",
  "solomonMCPServers",
  "solomonMCPAgents",
  "solomonMultiAgentGraphs",
  "heatmapAIReport",
  "geoAIReport",
];

collections.forEach((name) => {
  db.createCollection(name);
  print("Created collection: " + name);
});

// Create indexes for frequently queried fields
db.solomonChatHistory.createIndex({ ask_id: 1 });
db.solomonChatHistory.createIndex({ session_id: 1 });
db.solomonChatHistory.createIndex({ regDate: -1 });

db.solomonPromptHistory.createIndex({ deployStatus: 1 });

db.solomonMCPServers.createIndex({ name: 1 });
db.solomonMCPAgents.createIndex({ name: 1 });
db.solomonMCPAgents.createIndex({ agent: 1, isService: 1 });

db.solomonMultiAgentGraphs.createIndex({ name: 1 });
db.solomonMultiAgentGraphs.createIndex({ graphType: 1 });

print("MongoDB initialization complete for database: " + dbName);
