/**
 * Attaches a timestamp to the original event.
 *
 * @param {*} event The Cloud Functions event.
 * @param {function(*, *)} callback The callback function with
 * optional error and optional response.
 */
exports.handler = (event, callback) => {
  console.log(`My Cloud Function: ${event.data}`);
  response = {time: new Date(), originalData: event.data};
  callback(null, response);
};
