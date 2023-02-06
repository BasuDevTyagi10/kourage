const initializeBotLogger = require("./developmentLogger");
const initializeProductionLogger = require("./productionLogger");

let logger = null;

if (process.env.NODE_ENV === "production") {
  logger = initializeProductionLogger();
} else {
  logger = initializeBotLogger();
}

module.exports = logger;
