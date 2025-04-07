// src\migrations\011-auditTrails_migration.js
'use strict';

module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.createTable('auditTrails', {
      audit_id: {
        type: Sequelize.INTEGER,
        allowNull: false,
        primaryKey: true,
        autoIncrement: true
      },
      user_id: {
        type: Sequelize.INTEGER,
        allowNull: true,
      },
      visitor_id: {
        type: Sequelize.INTEGER,
        allowNull: true,
      },
      machineAddress: {
        type: Sequelize.STRING,
        allowNull: true
      },
      platform: {
        type: Sequelize.STRING,
        allowNull: true
      },

      userAgent: {
        type: Sequelize.STRING,
        allowNull: true
      },
      appVersion: {
        type: Sequelize.STRING,
        allowNull: true
      },
      vendor: {
        type: Sequelize.STRING,
        allowNull: true
      },
      place: {
        type: Sequelize.STRING,
        allowNull: true
      },
      latitude: {
        type: Sequelize.STRING,
        allowNull: true
      },
      longitude: {
        type: Sequelize.STRING,
        allowNull: true
      },

      current_url: {
        type: Sequelize.STRING,
        allowNull: true
      },
      previous_url: {
        type: Sequelize.STRING,
        allowNull: true
      },
      action: {
        type: Sequelize.STRING,
        allowNull: true
      },
      description: {
        type: Sequelize.TEXT,
        allowNull: true
      },
      createdAt: {
        allowNull: false,
        type: Sequelize.DATE,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP')
      },
      updatedAt: {
        allowNull: false,
        type: Sequelize.DATE,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
      }
    });
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.dropTable('audittrails');
  }
};
