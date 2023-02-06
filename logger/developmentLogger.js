const { createLogger, format, transports } = require("winston");
const { combine, timestamp, colorize, printf } = format;

const initializeBotLogger = () => {
  const myFormat = printf(({ level, message, timestamp }) => {
    return `[${timestamp}] ${level}: ${message}`;
  });
  return createLogger({
    level: "debug",
    format: combine(colorize(), timestamp({ format: "HH:mm:ss" }), myFormat),
    transports: [new transports.Console()],
  });
};

module.exports = initializeBotLogger;
