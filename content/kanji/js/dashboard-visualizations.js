/**
 * Dashboard Visualizations Module (dashboard-visualizations.js)
 *
 * Handles rendering of progress dashboard visualizations:
 * - Study heatmap (365-day calendar)
 * - Topic mastery rings (SVG)
 * - JLPT mastery bars
 * - Mastery trend line (8-week)
 * - At-risk kanji panel
 *
 * Part of Phase 2: Engagement Layer (Sprint 2)
 *
 * Version: v0.4.0
 * Updated: 2026-01-25
 *
 * TDD Reference: TDD-003 §6
 * PRD Reference: PRD-005
 * Tasks: T2.6, T2.7, T2.8
 */

const DashboardVisualizations = (function() {
  'use strict';

  // ============================================
  // Constants
  // ============================================

  // Heatmap colors (GitHub-style)
  const HEATMAP_COLORS = {
    0: '#ebedf0',  // No activity
    1: '#9be9a8',  // Light green (1-10 reviews)
    2: '#40c463',  // Medium green (11-25 reviews)
    3: '#30a14e',  // Dark green (26-50 reviews)
    4: '#216e39'   // Darkest green (51+ reviews)
  };

  // Topic colors
  const TOPIC_COLORS = {
    'home-life': '#3b82f6',   // Blue
    'shopping': '#22c55e',    // Green
    'restaurant': '#f59e0b',  // Amber
    'travel': '#8b5cf6'       // Purple
  };

  // JLPT level colors
  const JLPT_COLORS = {
    'N5': '#3b82f6',  // Blue
    'N4': '#22c55e',  // Green
    'N3': '#eab308',  // Yellow
    'N2': '#f97316',  // Orange
    'N1': '#ef4444'   // Red
  };

  // Day labels
  const DAY_LABELS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  // ============================================
  // Date Utilities
  // ============================================

  function getLocalDateString(date = new Date()) {
    return date.toLocaleDateString('en-CA'); // YYYY-MM-DD
  }

  function getMonthFromDate(dateStr) {
    return new Date(dateStr + 'T00:00:00').getMonth();
  }

  // ============================================
  // Study Heatmap (365-Day Calendar)
  // ============================================

  /**
   * Generate heatmap data for past 365 days
   *
   * @param {Object} dailyHistory - stats.daily_history object
   * @returns {Array} Array of day data objects
   */
  function generateHeatmapData(dailyHistory = {}) {
    const data = [];
    const today = new Date();

    for (let i = 364; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = getLocalDateString(date);

      const dayData = dailyHistory[dateStr] || { reviews: 0 };
      const reviews = dayData.reviews || 0;

      // Calculate intensity (0-4)
      let intensity = 0;
      if (reviews > 0) intensity = 1;
      if (reviews > 10) intensity = 2;
      if (reviews > 25) intensity = 3;
      if (reviews > 50) intensity = 4;

      data.push({
        date: dateStr,
        reviews,
        intensity,
        dayOfWeek: date.getDay(),
        month: date.getMonth(),
        isToday: i === 0
      });
    }

    return data;
  }

  /**
   * Render heatmap to container element
   *
   * @param {HTMLElement} container - Container element
   * @param {Object} dailyHistory - stats.daily_history object
   */
  function renderHeatmap(container, dailyHistory = {}) {
    const data = generateHeatmapData(dailyHistory);

    // Create wrapper
    const wrapper = document.createElement('div');
    wrapper.className = 'heatmap-wrapper';

    // Month labels
    const monthLabels = document.createElement('div');
    monthLabels.className = 'heatmap-month-labels';

    // Determine which months to show
    const monthsShown = new Set();
    let lastMonth = -1;

    data.forEach((day, index) => {
      if (day.dayOfWeek === 0 && day.month !== lastMonth) {
        monthsShown.add({ month: day.month, position: Math.floor(index / 7) });
        lastMonth = day.month;
      }
    });

    // Add month labels (simplified - show every ~4 weeks)
    const monthPositions = Array.from(monthsShown);
    monthPositions.forEach(({ month, position }) => {
      const label = document.createElement('span');
      label.className = 'month-label';
      label.textContent = MONTH_LABELS[month];
      label.style.gridColumn = position + 1;
      monthLabels.appendChild(label);
    });

    wrapper.appendChild(monthLabels);

    // Create grid container
    const gridContainer = document.createElement('div');
    gridContainer.className = 'heatmap-container';

    // Day labels
    const dayLabels = document.createElement('div');
    dayLabels.className = 'heatmap-day-labels';
    ['', 'Mon', '', 'Wed', '', 'Fri', ''].forEach(label => {
      const dayLabel = document.createElement('span');
      dayLabel.textContent = label;
      dayLabels.appendChild(dayLabel);
    });
    gridContainer.appendChild(dayLabels);

    // Heatmap grid
    const grid = document.createElement('div');
    grid.className = 'heatmap-grid';

    // Organize data into weeks/days grid
    // Grid is 7 rows (days) x 53 columns (weeks)
    const weeks = [];
    let currentWeek = [];

    // Fill in leading empty cells for first week
    const firstDayOfWeek = data[0].dayOfWeek;
    for (let i = 0; i < firstDayOfWeek; i++) {
      currentWeek.push(null);
    }

    data.forEach(day => {
      currentWeek.push(day);
      if (currentWeek.length === 7) {
        weeks.push(currentWeek);
        currentWeek = [];
      }
    });

    // Add remaining days
    if (currentWeek.length > 0) {
      while (currentWeek.length < 7) {
        currentWeek.push(null);
      }
      weeks.push(currentWeek);
    }

    // Render grid (column by column for CSS grid)
    weeks.forEach((week, weekIndex) => {
      week.forEach((day, dayIndex) => {
        const cell = document.createElement('div');
        cell.className = 'heatmap-cell';

        if (day) {
          cell.setAttribute('data-intensity', day.intensity);
          cell.setAttribute('data-date', day.date);
          cell.setAttribute('data-reviews', day.reviews);

          if (day.isToday) {
            cell.classList.add('today');
          }

          // Tooltip
          cell.title = `${day.date}: ${day.reviews} reviews`;
        } else {
          cell.classList.add('empty');
        }

        grid.appendChild(cell);
      });
    });

    gridContainer.appendChild(grid);
    wrapper.appendChild(gridContainer);

    // Legend
    const legend = document.createElement('div');
    legend.className = 'heatmap-legend';
    legend.innerHTML = `
      <span class="legend-label">Less</span>
      <span class="legend-cell" style="background: ${HEATMAP_COLORS[0]}"></span>
      <span class="legend-cell" style="background: ${HEATMAP_COLORS[1]}"></span>
      <span class="legend-cell" style="background: ${HEATMAP_COLORS[2]}"></span>
      <span class="legend-cell" style="background: ${HEATMAP_COLORS[3]}"></span>
      <span class="legend-cell" style="background: ${HEATMAP_COLORS[4]}"></span>
      <span class="legend-label">More</span>
    `;
    wrapper.appendChild(legend);

    // Clear and append
    container.innerHTML = '';
    container.appendChild(wrapper);
  }

  // ============================================
  // Topic Mastery Rings (SVG)
  // ============================================

  /**
   * Create SVG for circular progress ring
   *
   * @param {number} percentage - 0-100
   * @param {string} label - Topic name
   * @param {string} color - Ring color
   * @param {string} topicKey - Topic key for click handler
   * @returns {string} SVG markup
   */
  function createMasteryRing(percentage, label, color, topicKey = '') {
    const radius = 36;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;
    const displayPercent = Math.round(percentage);

    return `
      <div class="mastery-ring" data-topic="${topicKey}">
        <svg width="90" height="90" viewBox="0 0 90 90">
          <!-- Background circle -->
          <circle
            cx="45" cy="45" r="${radius}"
            fill="none" stroke="#e5e7eb" stroke-width="7"
          />
          <!-- Progress circle -->
          <circle
            cx="45" cy="45" r="${radius}"
            fill="none" stroke="${color}" stroke-width="7"
            stroke-dasharray="${circumference}"
            stroke-dashoffset="${offset}"
            stroke-linecap="round"
            transform="rotate(-90 45 45)"
            class="ring-progress"
          />
        </svg>
        <div class="ring-content">
          <div class="ring-percentage">${displayPercent}%</div>
          <div class="ring-label">${label}</div>
        </div>
      </div>
    `;
  }

  /**
   * Render topic mastery rings
   *
   * @param {HTMLElement} container - Container element
   * @param {Object} kanjiData - schema.kanji object
   */
  function renderTopicMasteryRings(container, kanjiData = {}) {
    const MasteryCalculator = window.MasteryCalculator;
    if (!MasteryCalculator) {
      container.innerHTML = '<p class="no-data">Mastery calculator not available</p>';
      return;
    }

    const topics = [
      { key: 'home-life', label: 'Home Life' },
      { key: 'shopping', label: 'Shopping' },
      { key: 'restaurant', label: 'Restaurant' },
      { key: 'travel', label: 'Travel' }
    ];

    let html = '<div class="mastery-rings-grid">';

    topics.forEach(topic => {
      const filtered = MasteryCalculator.filterByTopic(kanjiData, topic.key);
      const mastery = Object.keys(filtered).length > 0
        ? MasteryCalculator.calculateOverallMastery(filtered)
        : 0;
      const color = TOPIC_COLORS[topic.key] || '#64748b';

      html += createMasteryRing(mastery, topic.label, color, topic.key);
    });

    html += '</div>';
    container.innerHTML = html;
  }

  // ============================================
  // Mastery Trend Line (SVG)
  // ============================================

  /**
   * Generate trend line SVG
   *
   * @param {Array} snapshots - stats.mastery_snapshots array
   * @returns {string} SVG markup
   */
  function createTrendLine(snapshots = []) {
    const width = 320;
    const height = 120;
    const padding = 25;
    const rightPadding = 15;

    // Take last 8 weeks
    const data = snapshots.slice(-8);

    if (data.length < 2) {
      return `
        <div class="trend-no-data">
          <p>Not enough data yet</p>
          <p class="trend-hint">Check back after a week of studying!</p>
        </div>
      `;
    }

    // Scale points
    const graphWidth = width - padding - rightPadding;
    const graphHeight = height - padding * 2;
    const xStep = graphWidth / (data.length - 1);
    const yScale = graphHeight / 100;

    // Generate points
    const points = data.map((snapshot, i) => {
      const x = padding + i * xStep;
      const y = height - padding - (snapshot.overall * yScale);
      return { x, y, value: snapshot.overall, date: snapshot.date };
    });

    const pointsStr = points.map(p => `${p.x},${p.y}`).join(' ');

    // Create gradient fill area
    const areaPoints = [
      `${padding},${height - padding}`,
      ...points.map(p => `${p.x},${p.y}`),
      `${points[points.length - 1].x},${height - padding}`
    ].join(' ');

    return `
      <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" class="trend-svg">
        <defs>
          <linearGradient id="trendGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.3"/>
            <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.05"/>
          </linearGradient>
        </defs>

        <!-- Grid lines -->
        <line x1="${padding}" y1="${height - padding}" x2="${width - rightPadding}" y2="${height - padding}" stroke="#e5e7eb" stroke-width="1"/>
        <line x1="${padding}" y1="${padding}" x2="${padding}" y2="${height - padding}" stroke="#e5e7eb" stroke-width="1"/>

        <!-- Y-axis labels -->
        <text x="${padding - 5}" y="${padding + 4}" text-anchor="end" font-size="10" fill="#94a3b8">100%</text>
        <text x="${padding - 5}" y="${height - padding + 4}" text-anchor="end" font-size="10" fill="#94a3b8">0%</text>

        <!-- Area fill -->
        <polygon points="${areaPoints}" fill="url(#trendGradient)"/>

        <!-- Trend line -->
        <polyline
          points="${pointsStr}"
          fill="none"
          stroke="#3b82f6"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />

        <!-- Data points -->
        ${points.map(p => `
          <circle cx="${p.x}" cy="${p.y}" r="5" fill="#3b82f6" class="trend-point" data-value="${p.value.toFixed(1)}"/>
          <circle cx="${p.x}" cy="${p.y}" r="3" fill="white"/>
        `).join('')}
      </svg>
    `;
  }

  /**
   * Render trend line to container
   *
   * @param {HTMLElement} container - Container element
   * @param {Array} snapshots - stats.mastery_snapshots array
   */
  function renderTrendLine(container, snapshots = []) {
    const html = `
      <div class="trend-container">
        ${createTrendLine(snapshots)}
      </div>
    `;
    container.innerHTML = html;
  }

  // ============================================
  // At-Risk Kanji Panel
  // ============================================

  /**
   * Render at-risk kanji panel
   *
   * @param {HTMLElement} container - Container element
   * @param {Array} atRiskKanji - stats.at_risk_kanji array
   * @param {Array} kanjiMetadata - Full kanji metadata for lookups
   */
  function renderAtRiskPanel(container, atRiskKanji = [], kanjiMetadata = []) {
    if (!atRiskKanji || atRiskKanji.length === 0) {
      container.innerHTML = `
        <div class="at-risk-empty">
          <span class="at-risk-empty-icon">✨</span>
          <p>No at-risk kanji!</p>
          <p class="at-risk-hint">All your kanji are progressing well.</p>
        </div>
      `;
      return;
    }

    // Format stage names for display
    const formatStage = (stage) => {
      const stageNames = {
        'locked': 'Locked',
        'lesson': 'Lesson',
        'apprentice_1': 'App 1',
        'apprentice_2': 'App 2',
        'apprentice_3': 'App 3',
        'apprentice_4': 'App 4',
        'guru_1': 'Guru 1',
        'guru_2': 'Guru 2',
        'master': 'Master',
        'enlightened': 'Enlight',
        'burned': 'Burned'
      };
      return stageNames[stage] || stage;
    };

    // Limit to 10 most recent
    const displayKanji = atRiskKanji.slice(0, 10);

    let html = '<div class="at-risk-list">';

    displayKanji.forEach(item => {
      // Find metadata for this kanji
      const meta = kanjiMetadata.find(k => k.character === item.character);
      const meaning = meta?.meanings?.[0] || '';

      html += `
        <div class="at-risk-item" data-character="${item.character}">
          <span class="at-risk-kanji">${item.character}</span>
          <span class="at-risk-meaning">${meaning}</span>
          <span class="at-risk-drop">
            ${formatStage(item.dropped_from)} → ${formatStage(item.dropped_to)}
          </span>
          <button class="at-risk-review-btn" data-character="${item.character}" title="Review this kanji">
            ⟲
          </button>
        </div>
      `;
    });

    html += '</div>';

    if (atRiskKanji.length > 10) {
      html += `<p class="at-risk-more">+${atRiskKanji.length - 10} more</p>`;
    }

    container.innerHTML = html;
  }

  /**
   * Track at-risk kanji when stage drops
   *
   * @param {Object} schema - Full schema (will be mutated)
   * @param {string} character - Kanji character
   * @param {string} oldStage - Stage before review
   * @param {string} newStage - Stage after review
   * @returns {boolean} True if kanji was added to at-risk
   */
  function trackAtRiskKanji(schema, character, oldStage, newStage) {
    const STAGE_ORDER = [
      'locked', 'lesson', 'apprentice_1', 'apprentice_2',
      'apprentice_3', 'apprentice_4', 'guru_1', 'guru_2',
      'master', 'enlightened', 'burned'
    ];

    const oldIndex = STAGE_ORDER.indexOf(oldStage);
    const newIndex = STAGE_ORDER.indexOf(newStage);

    // Initialize array if needed
    if (!schema.stats.at_risk_kanji) {
      schema.stats.at_risk_kanji = [];
    }

    // If stage improved to guru_1 or higher, remove from at-risk
    const GURU_INDEX = STAGE_ORDER.indexOf('guru_1');
    if (newIndex >= GURU_INDEX && newIndex > oldIndex) {
      schema.stats.at_risk_kanji = schema.stats.at_risk_kanji.filter(
        k => k.character !== character
      );
      return false;
    }

    // Only track if stage dropped (not lessons going to apprentice)
    if (newIndex < oldIndex && oldIndex > 1) {
      const today = getLocalDateString();

      // Remove existing entry for this kanji
      schema.stats.at_risk_kanji = schema.stats.at_risk_kanji.filter(
        k => k.character !== character
      );

      // Add new at-risk entry at beginning
      schema.stats.at_risk_kanji.unshift({
        character,
        dropped_from: oldStage,
        dropped_to: newStage,
        date: today
      });

      // Keep max 50 entries
      if (schema.stats.at_risk_kanji.length > 50) {
        schema.stats.at_risk_kanji = schema.stats.at_risk_kanji.slice(0, 50);
      }

      // Clean up entries older than 7 days
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      const weekAgoStr = getLocalDateString(weekAgo);

      schema.stats.at_risk_kanji = schema.stats.at_risk_kanji.filter(
        k => k.date >= weekAgoStr
      );

      return true;
    }

    return false;
  }

  // ============================================
  // Stats Summary Panel
  // ============================================

  /**
   * Render stats summary panel
   *
   * @param {HTMLElement} container - Container element
   * @param {Object} schema - Full schema object
   */
  function renderStatsSummary(container, schema) {
    if (!schema || !schema.stats) {
      container.innerHTML = '<p class="no-data">No stats available</p>';
      return;
    }

    const stats = schema.stats;
    const kanjiCount = Object.keys(schema.kanji || {}).length;

    // Calculate burned count
    let burnedCount = 0;
    Object.values(schema.kanji || {}).forEach(k => {
      if (k.srs?.stage === 'burned') burnedCount++;
    });

    // Calculate accuracy from today's stats
    const todayReviews = stats.today?.reviews_completed || 0;
    const todayCorrect = stats.today?.correct_count || 0;
    const todayAccuracy = todayReviews > 0
      ? Math.round((todayCorrect / todayReviews) * 100)
      : 0;

    const html = `
      <div class="stats-summary-grid">
        <div class="summary-stat">
          <div class="summary-stat-value">${(stats.total_reviews || 0).toLocaleString()}</div>
          <div class="summary-stat-label">Total Reviews</div>
        </div>
        <div class="summary-stat">
          <div class="summary-stat-value">${burnedCount}</div>
          <div class="summary-stat-label">Kanji Mastered</div>
        </div>
        <div class="summary-stat">
          <div class="summary-stat-value">${todayAccuracy}%</div>
          <div class="summary-stat-label">Today's Accuracy</div>
        </div>
        <div class="summary-stat">
          <div class="summary-stat-value">${stats.total_kanji_seen || 0}</div>
          <div class="summary-stat-label">Kanji Seen</div>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  // ============================================
  // Weekly Snapshot Management
  // ============================================

  /**
   * Check if a weekly snapshot should be taken
   *
   * @param {Array} snapshots - Existing snapshots array
   * @returns {boolean} True if snapshot should be taken
   */
  function shouldTakeWeeklySnapshot(snapshots = []) {
    if (snapshots.length === 0) return true;

    const lastSnapshot = snapshots[snapshots.length - 1];
    const lastDate = new Date(lastSnapshot.date + 'T00:00:00');
    const today = new Date();

    // Get days since last snapshot
    const daysDiff = Math.floor((today - lastDate) / (24 * 60 * 60 * 1000));

    return daysDiff >= 7;
  }

  /**
   * Take a weekly mastery snapshot
   *
   * @param {Object} schema - Full schema (will be mutated)
   * @param {Object} MasteryCalculator - MasteryCalculator module
   * @returns {Object} New snapshot object
   */
  function takeWeeklySnapshot(schema, MasteryCalculator) {
    if (!schema || !MasteryCalculator) return null;

    const kanjiData = schema.kanji || {};
    const today = getLocalDateString();

    const snapshot = {
      date: today,
      overall: MasteryCalculator.calculateOverallMastery(kanjiData),
      n5: MasteryCalculator.calculateJLPTMastery(kanjiData, 'N5'),
      n4: MasteryCalculator.calculateJLPTMastery(kanjiData, 'N4'),
      n3: MasteryCalculator.calculateJLPTMastery(kanjiData, 'N3'),
      n2: MasteryCalculator.calculateJLPTMastery(kanjiData, 'N2')
    };

    // Initialize array if needed
    if (!schema.stats.mastery_snapshots) {
      schema.stats.mastery_snapshots = [];
    }

    // Add snapshot
    schema.stats.mastery_snapshots.push(snapshot);

    // Keep max 52 snapshots (1 year)
    if (schema.stats.mastery_snapshots.length > 52) {
      schema.stats.mastery_snapshots = schema.stats.mastery_snapshots.slice(-52);
    }

    return snapshot;
  }

  // ============================================
  // Daily History Update
  // ============================================

  /**
   * Update daily history with review data
   *
   * @param {Object} schema - Full schema (will be mutated)
   * @param {number} reviews - Number of reviews completed
   * @param {number} correct - Number correct
   * @param {number} xpEarned - XP earned
   */
  function updateDailyHistory(schema, reviews = 0, correct = 0, xpEarned = 0) {
    const today = getLocalDateString();

    if (!schema.stats.daily_history) {
      schema.stats.daily_history = {};
    }

    const existing = schema.stats.daily_history[today] || {
      reviews: 0,
      correct: 0,
      xp_earned: 0
    };

    schema.stats.daily_history[today] = {
      reviews: existing.reviews + reviews,
      correct: existing.correct + correct,
      xp_earned: existing.xp_earned + xpEarned
    };

    // Prune history older than 400 days
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 400);
    const cutoffStr = getLocalDateString(cutoffDate);

    Object.keys(schema.stats.daily_history).forEach(date => {
      if (date < cutoffStr) {
        delete schema.stats.daily_history[date];
      }
    });
  }

  // ============================================
  // Public API
  // ============================================

  return {
    // Constants
    HEATMAP_COLORS,
    TOPIC_COLORS,
    JLPT_COLORS,

    // Heatmap
    generateHeatmapData,
    renderHeatmap,

    // Mastery Rings
    createMasteryRing,
    renderTopicMasteryRings,

    // Trend Line
    createTrendLine,
    renderTrendLine,

    // At-Risk Panel
    renderAtRiskPanel,
    trackAtRiskKanji,

    // Stats Summary
    renderStatsSummary,

    // Snapshot Management
    shouldTakeWeeklySnapshot,
    takeWeeklySnapshot,

    // Daily History
    updateDailyHistory,

    // Utilities
    getLocalDateString
  };
})();

// Export for browser use
if (typeof window !== 'undefined') {
  window.DashboardVisualizations = DashboardVisualizations;
}

// Export for Node.js/testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DashboardVisualizations;
}
