const Joi = require('joi');

const validateTask = (data) => {
  const schema = Joi.object({
    title: Joi.string().min(3).max(100).required(),
    description: Joi.string().max(500).allow(''),
    // Ensure assignedTo is a valid MongoDB ObjectId
    assignedTo: Joi.string().regex(/^[0-9a-fA-F]{24}$/).required().messages({
      'string.pattern.base': 'Invalid User ID format'
    }),
    status: Joi.string().valid('pending', 'completed')
  });

  return schema.validate(data);
};

const validateId = (id) => {
  const schema = Joi.string().regex(/^[0-9a-fA-F]{24}$/).required().messages({
    'string.pattern.base': 'Invalid ID format'
  });

  return schema.validate(id);
};

module.exports = { validateTask, validateId };
