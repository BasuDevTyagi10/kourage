const { EmbedBuilder } = require("discord.js");
const path = require("path");
const fs = require("fs");
require('dotenv').config()

const logger = require("./logger");
const { getReviews } = require("./scrapper");
const { info } = require("console");


/**
 * This function fetch the google reviews after every 12 hours and send the latest reviews on discord channel.
 * @param {*} discordClient "Object of discord client."
 */

const startInterval = async (discordClient) => {
  try {
    const { reviews } = await getReviews();
    if (reviews?.length) {
      logger.info(
        "Scrapping successfully done!"
      );
    }
    const fileReviews = await readFromFile();
    if (fileReviews === null) {
      logger.info(
        "Sending All review first time"
      );
      sendMessage(reviews, discordClient);
      writeInFile(reviews);
    } else if (reviews?.length > fileReviews.length) {
      writeInFile(reviews);
      const noOfLatestReview = reviews?.length - fileReviews?.length;
      let count = 0;
      let latestReviewsList = [];

      for (let i = 0; i < reviews.length; i++) {
        let flag = false;
        for (let j = 0; j < fileReviews.length; j++) {
          if (reviews[i]?.user?.name === fileReviews[j]?.user?.name) {
            flag = true;
          }
        }
        if (!flag) { latestReviewsList.push(reviews[i]); count++; }
        if (count > noOfLatestReview) {
          break;
        }
      }
      logger.info(`Find ${latestReviewsList.length} latest review`);
      sendMessage(latestReviewsList, discordClient);
    }
    setTimeout(startInterval, 43200000);
  } catch (error) {
    logger.error("Error in startInterval:", error);
  }
};

/**
 * Send reviews to discord channel.
 * @param {*} reviews Array of reviews objects.
 * @param {*} discordClient Discord client object.
 */

const sendMessage = async (reviews, discordClient) => {
  try {
    if (reviews?.length) {
      logger.info("Get latest review array");
    const channel = discordClient.channels.cache.get(process.env.CHANNEL_ID);
      reviews?.forEach(async (element) => {
        const redirectUrl = element?.user?.thumbnail ? element?.user?.thumbnail : element?.user?.link;
        if (!element?.snippet) element["snippet"] = "None";
        if (element?.user?.name) {
          const reviewEmbed = new EmbedBuilder()
            .setColor(0x0099ff)
            .setTitle("⭐".repeat(element?.rating))
            .setAuthor({
              name: element?.user?.name,
              iconURL: element?.user?.url,
              url: redirectUrl,
            })
            .setDescription(element?.snippet);
          const res = await channel.send({ embeds: [reviewEmbed] });
          if (res.status === 200) {
            logger.info("Embed send successfully!")
          }
        }
      });
      logger.info("Reviews send successfully on discord channel");
    }
  } catch (error) {
    logger.error("Error in 'sendMessage' func and error is:", error);
  }
};

const readFromFile = () => {
  const filePath = path.join(__dirname, "review.json");
  return new Promise((resolve, reject) => {
    try {
      fs.readFile(filePath, "utf8", async (err, jsonString) => {
        if (err) {
          logger.error(
            "Error in readFromFile func during file reading and error is",
            err
          );
          return resolve(null);
        } else {
          let data = null;
          if (jsonString) data = JSON.parse(jsonString);
          logger.info("File read successfully!");
          return resolve(data);
        }
      });
    } catch (error) {
      logger.error("Error in readFromFile func and error is", error);
      resolve(null);
    }
  });
};

const writeInFile = (data) => {
  const filePath = path.join(__dirname, "review.json");
  return new Promise((resolve, reject) => {
    try {
      fs.writeFile(filePath, JSON.stringify(data), (err) => {
        if (err) {
          logger.error("Error in writeInFile func and error is:", err);
        } else {
          logger.info("File write successfully!");
          resolve(true);
        }
      });
    } catch (error) {
      logger.error("Error in writeInFile func and error is", error);
      resolve(false);
    }
  });
};

const sleep = (time) => {
  return new Promise((resolve) => {
    setTimeout(resolve, time);
  })
}

module.exports = { startInterval };
