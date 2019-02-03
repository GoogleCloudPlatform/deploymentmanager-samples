/**
 * Responds to any HTTP request that can provide a "message" field in the body.
 *
 * @param {Object} req Cloud Function request context.
 * @param {Object} res Cloud Function response context.
 */
exports.handler = function(req, res) {
  console.log(req.body.message);
  res.status(200).send(
      {hello: 'world', time: new Date(), codeHash: process.env.codeHash});
};
