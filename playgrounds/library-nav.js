/**
 * Learning Playground - Library Navigation Module
 * Provides topic and section organization for the learning content
 */

window.LibraryNav = {
  /**
   * Get all available topics organized by section
   * @returns {Array} Array of topic objects with {id, title, section}
   */
  getTopics: () => {
    return [
      // Getting Started Section
      { id: 'intro', title: 'Welcome to dbt', section: 'Getting Started' },
      { id: 'philosophy', title: 'The Analytics Engineering Philosophy', section: 'Getting Started' },
      { id: 'setup', title: 'Setting Up Your dbt Project', section: 'Getting Started' },

      // Core Concepts Section
      { id: 'models', title: 'dbt Models Fundamentals', section: 'Core Concepts' },
      { id: 'staging', title: 'Staging Layer Pattern', section: 'Core Concepts' },
      { id: 'intermediate', title: 'Intermediate Transformations', section: 'Core Concepts' },
      { id: 'marts', title: 'Marts & Final Layer', section: 'Core Concepts' },
      { id: 'ctes', title: 'CTEs for Readability', section: 'Core Concepts' },

      // Best Practices Section
      { id: 'naming', title: 'Naming Conventions', section: 'Best Practices' },
      { id: 'testing', title: 'Testing Data Quality', section: 'Best Practices' },
      { id: 'documentation', title: 'Documenting Your Models', section: 'Best Practices' },
      { id: 'performance', title: 'Query Performance Optimization', section: 'Best Practices' },
      { id: 'versioning', title: 'Model Versioning', section: 'Best Practices' },

      // Advanced Topics Section
      { id: 'macros', title: 'Writing Custom Macros', section: 'Advanced Topics' },
      { id: 'dependencies', title: 'Managing Model Dependencies', section: 'Advanced Topics' },
      { id: 'incremental', title: 'Incremental Models', section: 'Advanced Topics' },
      { id: 'snapshots', title: 'Snapshots for SCD Type 2', section: 'Advanced Topics' },
      { id: 'packages', title: 'Using dbt Packages', section: 'Advanced Topics' },

      // Workflow Section
      { id: 'cli', title: 'dbt CLI Commands', section: 'Workflow' },
      { id: 'debugging', title: 'Debugging & Troubleshooting', section: 'Workflow' },
      { id: 'deployment', title: 'Deploying to Production', section: 'Workflow' },
      { id: 'monitoring', title: 'Monitoring & Alerts', section: 'Workflow' },
    ];
  },

  /**
   * Get topics organized by section for nav rendering
   * @returns {Array} Array of section objects with {section, topics: []}
   */
  getTopicsBySection: () => {
    const topics = window.LibraryNav.getTopics();
    const sections = {};

    topics.forEach(topic => {
      if (!sections[topic.section]) {
        sections[topic.section] = [];
      }
      sections[topic.section].push(topic);
    });

    // Return in a specific order
    const sectionOrder = ['Getting Started', 'Core Concepts', 'Best Practices', 'Advanced Topics', 'Workflow'];
    return sectionOrder.map(section => ({
      section,
      topics: sections[section] || []
    }));
  },

  /**
   * Get a single topic by ID
   * @param {string} topicId - The topic ID
   * @returns {Object|null} Topic object or null if not found
   */
  getTopic: (topicId) => {
    const topics = window.LibraryNav.getTopics();
    return topics.find(t => t.id === topicId) || null;
  }
};
