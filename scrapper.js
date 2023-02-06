const puppeteer = require("puppeteer");
const logger = require("./logger");

const placeUrl =
  "https://www.google.com/maps/place/Koders/@30.3307776,77.9591553,17z/data=!3m1!4b1!4m5!3m4!1s0x39092b338ee9e6f1:0x5964dd90fecf95d2!8m2!3d30.3307776!4d77.961344";

async function scrollPage(page, scrollContainer) {
  try {
    logger.info("scrollPage func running!");
    let lastHeight = await page.evaluate(
      `document.querySelector("${scrollContainer}").scrollHeight`
    );
    while (true) {
      await page.evaluate(
        `document.querySelector("${scrollContainer}").scrollTo(0, document.querySelector("${scrollContainer}").scrollHeight)`
      );
      await page.waitForTimeout(3000);
      let newHeight = await page.evaluate(
        `document.querySelector("${scrollContainer}").scrollHeight`
      );
      if (newHeight === lastHeight) {
        break;
      }
      lastHeight = newHeight;
    }
  } catch (error) {
    logger.error("Error in scrollPage func and error is:", error);
  }
}

async function getReviewsFromPage(page) {
  try {
    const reviews = await page.evaluate(() => {
      return Array.from(document.querySelectorAll(".jftiEf")).map((el) => {
        return {
          user: {
            name: el.querySelector(".d4r55")?.textContent.trim(),
            link: el.querySelector(".WNxzHc a")?.getAttribute("href"),
            url: el.querySelector(".NBa7we")?.getAttribute("src"),
            localGuide:
              el.querySelector(".RfnDt span:first-child")?.style.display ===
              "none"
                ? undefined
                : true,
            reviews: parseInt(
              el
                .querySelector(".RfnDt span:last-child")
                ?.textContent.replace("·", "")
            ),
          },
          rating: parseFloat(
            el.querySelector(".kvMYJc")?.getAttribute("aria-label")
          ),
          date: el.querySelector(".rsqaWe")?.textContent.trim(),
          snippet: el.querySelector(".MyEned")?.textContent.trim(),
          likes: parseFloat(
            el.querySelector(".GBkF3d:nth-child(2)")?.getAttribute("aria-label")
          ),
          images: Array.from(el.querySelectorAll(".KtCyie button")).length
            ? Array.from(el.querySelectorAll(".KtCyie button")).map((el) => {
                return {
                  thumbnail: getComputedStyle(el).backgroundImage.slice(5, -2),
                };
              })
            : undefined,
          date: el.querySelector(".rsqaWe")?.textContent.trim(),
        };
      });
    });
    return reviews;
  } catch (error) {
    logger.error("Error in 'getReviewsFromPage' function and error is:", error);
  }
}

async function getPageUrl(page) {
  try {
    logger.info("Start scrapping thumbnail...!");
    return await page.evaluate(async () => {
      const urls = [];
      const tempArr = [...document.querySelectorAll(".GBkF3d")];
      for (let i = 0; i < tempArr.length; i++) {
        if (i % 2 !== 0) {
          tempArr[i].click();
          function sleep(time) {
            return new Promise((resolve) => {
              setTimeout(resolve, time);
            });
          }
          await sleep(3000);
          urls.push(document.querySelectorAll(".vrsrZe")[0].value);
          document.querySelectorAll(".AmPKde")[0].click();
        }
      }
      return urls;
    });
  } catch (error) {
    logger.error("Error in 'getPageUrl' function and error is:", error);
  }
}

// Currently Out of scop
// async function fillPlaceInfo(page) {
//   const placeInfo = await page.evaluate(() => {
//     return {
//       title: document.querySelector(".DUwDvf")?.textContent.trim(),
//       address: document
//         .querySelector("button[data-item-id='address']")
//         ?.textContent.trim(), // data-item-id attribute may be different if the language is not English
//       rating: (() => {
//         const str = document.querySelector("div.F7nice")?.textContent.trim();
//         return str.substring(0, 3);
//       })(),
//       reviews: (() => {
//         const str = document.querySelector("div.F7nice")?.textContent.trim();
//         return str.substring(3, str.length);
//       })(),
//     };
//   });
//   return placeInfo;
// }

async function getLocalPlaceReviews() {
  try {
    let browser = null;
    if (process.platform === "darwin") {
      browser = await puppeteer.launch({
        headless: true,
        executablePath:
          "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        args: ["--no-sandbox", "--disable-setuid-sandbox"],
      });
    } else {
      browser = await puppeteer.launch({
        headless: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox"],
      });
    }

    const page = await browser.newPage();

    await page.setDefaultNavigationTimeout(60000);
    await page.goto(placeUrl);
    await page.waitForSelector(".DUwDvf");
    // Use if wants to get place info
    // const placeInfo = await fillPlaceInfo(page);
    await page.click(".F7nice");
    await page.waitForTimeout(2000);
    await page.waitForSelector(".W1neJ");
    await scrollPage(
      page,
      ".w6VYqd > .tTVLSc > .k7jAl > .e07Vkf > .aIFcqe > .m6QErb > .m6QErb"
    );
    let reviews = await getReviewsFromPage(page);
    if (reviews?.length) {
      const url = await getPageUrl(page);
      reviews = reviews.map((item, i) => {
        if (i < url?.length)
          return {
            ...item,
            snippet: item?.snippet.replace("More", ""),
            user: {
              ...item.user,
              thumbnail: url[i],
            },
          };
        else
          return {
            ...item,
            user: {
              ...item.user,
              thumbnail: item?.user?.link,
            },
          };
      });
    } else reviews = [];
    await browser.close();
    return { placeInfo: {}, reviews };
  } catch (error) {
    logger.error("Error in func getLocalPlaceReviews and error is:", error);
  }
}

const getReviews = async () => {
  logger.info("Scrapping start");
  return await getLocalPlaceReviews();
};
module.exports = { getReviews };
