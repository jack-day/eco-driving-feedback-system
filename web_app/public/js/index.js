/** @module */
/* global Chart */
import initCoreUI from './modules/coreUI.js';
import { authorize, removeAuthLoader } from './modules/auth0.js';

const el = {};
let accessToken;
let performanceGraph;

/** Factor information */
const factors = {
    ecoDriving: {
        name: 'Overall Eco-Driving Performance',
        desc: 'Eco-driving performance calculated across all factors.',
    },
    drivAccSmoothness: {
        name: 'Driving Acceleration Smoothness',
        desc: 'Smoothness of acceleration whilst driving.',
        tip: `Your acceleration whilst driving is harsh, try accelerating slower
        to smoothen your speed changes and prevent expending uneeded energy.`,
    },
    startAccSmoothness: {
        name: 'Starting Acceleration Smoothness',
        desc: 'Smoothness of acceleration from being stopped.',
        tip: `Your acceleration from being stopped is harsh, try accelerating
        slower to smoothen your speed changes and prevent expending uneeded energy.`,
    },
    decSmoothness: {
        name: 'Deceleration Smoothness',
        desc: 'Smoothness of deceleration.',
        tip: `Your deceleration is harsh, try deceleration slower to smoothen
        your speed changes and prevent expending uneeded energy. Use engine
        braking through lower gears and attempt to use less foot brake to
        maintain speed and prevent frequent decelaration and acceleration.`,
    },
    gsiAdh: {
        name: 'Gear Shift Indicator Adherence',
        desc: 'Consistency of upshifting when indicated to do so by the device.',
        tip: `You're not upshfiting gears when indicated to by the device. Try
        upshifting when indicated to stay within the most efficient RPM range.`,
    },
    speedLimitAdh: {
        name: 'Speed Limit Adherence',
        desc: 'Consistency of keeping vehicle speed below the speed limit.',
        tip: `You're regularly going above the speed limit. Keep within the
        speed limit as higher speeds result in higher fuel consumption. Your
        safety is also more important than anything, speeding is dangerous.`,
    },
    motorwaySpeed: {
        name: 'Motorway Speed',
        desc: 'Average vehicle speed on motorways',
        tip: `Your average motorway speed is too fast. Higher speeds result in
        higher fuel consumption and this is even more prominent on motorways.
        Stay below 70mph and try to stay closer to 65 or even 60mph.`,
    },
    idleDuration: {
        name: 'Idling Duration',
        desc: 'Average duration of time spent with the engine on whilst not moving.',
        tip: `You're average idling duration is too long. Try switching off your
        engine when idling for periods longer than 10-30s.`,
    },
    journeyIdlePct: {
        name: 'Percentage of Journey Time Spent Idling',
        desc: 'Average time spent idling per journey',
        tip: `You're spending too much of your journey idling. Try choosing a
        less congested route, leaving at a different time or switching off your
        engine when idling for periods longer than 10-30s.`,
    },
    journeyDistance: {
        name: 'Journey Distance',
        desc: 'Average journey distance.',
        tip: `The average distance of your journeys is too short. Try using
        alternative methods of travel such as walking, cycling or public
        transport for short journeys.`,
    },
};


// Eco-Driving Performance
// ----------------------------------------------
/**
 * Animates an element to count from 0 to a given number
 * @param {HTMLElement} elem - The element to animate
 * @param {number} target - The target number the counter should count to and finish at
 * @param {number} duration - The duration of the entire animation in milliseconds
 */
function animateCounter(elem, target, duration) {
    elem.textContent = 0;
    const animate = setInterval(() => {
        const currVal = parseInt(elem.textContent);
        if (target && currVal < target) {
            elem.textContent = currVal + 1;
        } else {
            clearInterval(animate);
        }
    }, duration / target);
}

/** Intialise the Eco-Driving Performance section */
function initEcoDrivingPerformance(ecoDrivingScore) {
    el.ecoDrivingScore.style = `--score: ${ecoDrivingScore}`;
    animateCounter(el.scoreValue, ecoDrivingScore, 1000);

    let filename;
    if (0 <= ecoDrivingScore && ecoDrivingScore <= 20) {
        filename = '0_to_20.png';
    } else if (20 < ecoDrivingScore && ecoDrivingScore <= 40) {
        filename = '20_to_40.png';
    } else if (40 < ecoDrivingScore && ecoDrivingScore <= 60) {
        filename = '40_to_60.png';
    } else if (60 < ecoDrivingScore && ecoDrivingScore <= 80) {
        filename = '60_to_80.png';
    } else if (80 < ecoDrivingScore && ecoDrivingScore <= 100) {
        filename = '80_to_100.png';
    }

    el.scoreImg.src = filename ? `/assets/img/plant/${filename}` : '';
}


// Behaviours to Improve
// ----------------------------------------------
/** Add behaviour tip to Behaviours to Improve */
function addBehaviourTip(behaviourName) {
    const li = document.createElement('li');
    const article = document.createElement('article');
    const title = document.createElement('h4');
    const tip = document.createElement('p');

    title.textContent = factors[behaviourName].name;
    tip.textContent = factors[behaviourName].tip;

    article.append(title, tip);
    li.append(article);
    el.behavioursToImprove.append(li);
}

/**
 * Intialise the Behaviours to Improve section 
 * @returns The top behaviour needing to be improved
 */
function initBehavioursToImprove(latestScores) {
    const behaviours = [];

    for (const [name, score] of Object.entries(latestScores)) {
        if (name !== 'calculatedAt' && name !== 'ecoDriving') {
            behaviours.push({ name, score });
        }
    }

    behaviours.sort((a, b) => a.score - b.score);

    for (let i = 0; i < 3; i++) {
        addBehaviourTip(behaviours[i].name);
    }

    return behaviours[0].name;
}


// Journeys
// ----------------------------------------------
/** Gets the next 10 journeys */
async function fetchJourneys() {
    const limit = 10;
    const offset = parseInt(el.journeys.dataset.offset);
    const response = await fetch(`/api/journeys?limit=${limit}&offset=${offset}`, {
        headers: {
            'Authorization': `Bearer ${accessToken}`,
        },
    });

    if (response.ok) {
        const journeys = await response.json();

        if (response.headers.get('More-Entries') === 'true') {
            el.journeys.dataset.offset = offset + limit;
        } else {
            el.journeysLoadMore.remove();
            el.journeys.dataset.complete = '';
        }

        return journeys;
    } else {
        throw Error('Failed to fetch journeys');
    }
}

/** Create a table cell with a given value */
function createTableCell(value) {
    const cell = document.createElement('td');
    cell.textContent = value;
    return cell;
}

/** Format a timestamp into the format of DD/MM/YY HH:MM */
function formatTimestamp(ts) {
    ts = new Date(ts);
    return `${ts.toLocaleString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: '2-digit',
    })} ${ts.toLocaleTimeString('en-GB', { timeStyle: 'short' })}`;
}

/** Format a duration of seconds into the format of '{hours}h {mins}m {secs}s' */
function formatDuration(seconds) {
    const min = 60 * 1;
    const hour = 60 * min;

    const hours = Math.floor(seconds / hour);
    const mins = Math.floor((seconds % hour) / min);
    const secs = Math.floor(((seconds % hour) % min));

    let duration = '';
    if (hours > 0) duration += `${hours}h `;
    if (mins > 0) duration += `${mins}m `;
    duration += `${secs}s`;
    return duration;
}

/** Add a journey to the journeys table */
function addJourney(journey) {
    const row = document.createElement('tr');

    const start = createTableCell(formatTimestamp(journey.start));
    const end = createTableCell(formatTimestamp(journey.end));
    const distance = createTableCell(`${journey.distance}km`);
    const idleSecs = createTableCell(formatDuration(journey.idleSecs));
    const gsiAdh = createTableCell(`${journey.gsiAdh}%`);

    row.append(start, end, distance, idleSecs, gsiAdh);
    el.journeysTBody.append(row);
}

/** Get more journeys and add them to the journeys table */
async function updateJourneys() {
    const journeys = await fetchJourneys();
    journeys.forEach(addJourney);
}

/** Initialise Journeys section */
async function initJourneys() {
    await updateJourneys();
    el.journeysLoadMore.addEventListener('click', async () => {
        const origText = el.journeysLoadMore.textContent;
        el.journeysLoadMore.textContent = 'Loading...';

        try {
            await updateJourneys();
            el.journeysContainer.classList.remove('error');
        } catch (err) {
            el.journeysContainer.classList.add('error');
        } finally {
            el.journeysLoadMore.textContent = origText;
        }
    });
}


// Performance
// ----------------------------------------------
/** Get the most latest/most recent scores  */
async function getFactorScores(type, maxDaysAgo) {
    let maxDaysAgoQuery;
    
    if (maxDaysAgo === 'All') {
        maxDaysAgoQuery = '';
    } else {
        maxDaysAgoQuery = `&maxDaysAgo=${maxDaysAgo}`;
    }

    const response = await fetch(`/api/scores?type=${type}${maxDaysAgoQuery}`, {
        headers: {
            'Authorization': `Bearer ${accessToken}`,
        },
    });

    if (response.ok) {
        const scores = await response.json();
        return scores;
    } else {
        throw Error('Failed to fetch factor scores');
    }
}

/** Get the currently selected max days ago from the performance time menu */
function getSelectedMaxDaysAgo() {
    for (const item of el.performanceTimeMenuItems) {
        if (item.dataset.selected != undefined) {
            return item.dataset.maxDaysAgo;
        }
    }
}

/** Get the currently selected factor */
function getSelectedFactor() {
    for (const item of el.performanceFactorMenuItems) {
        if (item.dataset.selected) {
            return item.dataset.factor;
        }
    }
}

/** Show there has been an error in the performance section */
function showPerformanceError() {
    el.performance.classList.add('error');
    el.performanceFactorScore.textContent = '-';
}

/** Hide any error messages in the performance section */
function hidePerformanceError() {
    el.performance.classList.remove('error');
}

/** Update the current score */
function updateScore(score) {
    if (score != undefined) {
        animateCounter(el.performanceFactorScore, score, 500);
    } else {
        el.performanceFactorScore.textContent = '-';
    }
}

/** Get the step size in months for the performance graph */
function getMonthStepSize() {
    const maxDaysAgo = getSelectedMaxDaysAgo();
    if (maxDaysAgo === '30' || maxDaysAgo === '91') {
        return 1;
    } else if (maxDaysAgo === '183' || maxDaysAgo === '365') {
        return 3;
    } else {
        return 6;
    }
}

/** Updates the performance graph with new scores */
function updatePerformanceGraph(scores, factorName) {
    if (performanceGraph) performanceGraph.destroy();
    const style = getComputedStyle(document.body);
    const graphStyle = getComputedStyle(el.performanceGraph);
    const primaryColor = style.getPropertyValue('--primary');
    const textColor = graphStyle.getPropertyValue('--text-color');
    const gridColor = graphStyle.getPropertyValue('--grid-color');

    performanceGraph = new Chart(el.performanceGraphCtx, {
        type: 'line',
        data: {
            datasets: [{
                data: scores,
                borderColor: primaryColor,
                tension: 0,
                fill: false,
                spanGaps: true,
            }],
        },
        options: {
            parsing: {
                xAxisKey: 'calculatedAt',
                yAxisKey: factorName,
            },
            scales: {
                x: {
                    type: 'timeseries',
                    max: new Date().toISOString(),
                    time: {
                        unit: 'month',
                        stepSize: getMonthStepSize(),
                        displayFormats: {
                            'month': 'dd/MM',
                        },
                    },
                    ticks: {
                        color: textColor,
                        autoSkipPadding: 50,
                    },
                    grid: {
                        borderColor: textColor,
                        display: false,
                    },
                },
                y: {
                    type: 'linear',
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        padding: 8,
                        color: textColor,
                    },
                    grid: {
                        borderColor: textColor,
                        color: gridColor,
                        tickLength: 0,
                    },
                },
            },
            plugins: {
                legend: {
                    display: false,
                },
            },
        },
    });
}

/** Set the current behaviour being analysed in the Performance section */
async function setPerformanceFactor(name) {
    // Set loading placeholders whilst fetching
    el.performanceFactorNameH3.textContent = 'Loading...';
    el.performanceFactorDesc.textContent = '';
    el.performanceFactorScore.textContent = '-';

    // Fetch and update details
    try {
        const scores = await getFactorScores(name, getSelectedMaxDaysAgo());
        hidePerformanceError();
        el.performanceFactorNameH3.textContent = factors[name].name;
        el.performanceFactorDesc.textContent = factors[name].desc;
        updateScore(scores[0][name]);
    
        // Update menu
        for (const menuItem of el.performanceFactorMenuItems) {
            if (menuItem.dataset.factor === name) {
                menuItem.dataset.selected = true;
            } else {
                delete menuItem.dataset.selected;
            }
        }
    
        updatePerformanceGraph(scores, name);
    } catch (err) {
        showPerformanceError();
        const currFactor = getSelectedFactor();
        el.performanceFactorNameH3.textContent = factors[currFactor].name;
        el.performanceFactorDesc.textContent = factors[currFactor].desc;
    }
}

/** Add a factor to the performance factor menu */
function addFactorToMenu(shortName, data) {
    const clone = el.performanceFactorMenuItemTmpl.content.cloneNode(true);
    const li = clone.querySelector('li');
    const span = clone.querySelector('span');

    span.textContent = data.name;
    li.dataset.factor = shortName;
    li.addEventListener('click', () => {
        if (!li.dataset.selected) {
            setPerformanceFactor(shortName);
        }
        el.performanceFactorMenu.classList.add('hide');
        el.performanceFactorNameIcon.classList.remove('open');
    });

    el.performanceFactorMenu.append(clone);
    return li;
}

/** Initialise the performance factor selection menu */
function initPerformanceFactorMenu() {
    // Initialise list with factors
    const items = [];

    for (const [shortName, data] of Object.entries(factors)) {
        items.push(addFactorToMenu(shortName, data));
    }

    el.performanceFactorMenuItems = items;

    
    // Add listeners to open/close the menu
    el.performanceFactorName.addEventListener('click', () => {
        el.performanceFactorMenu.classList.toggle('hide');
        el.performanceFactorNameIcon.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
        if (
            e.target !== el.performanceFactorMenu &&
            e.target !== el.performanceFactorNameH3 &&
            e.target !== el.performanceFactorNameIcon &&
            !el.performanceFactorMenu.classList.contains('hide')
        ) {
            el.performanceFactorMenu.classList.add('hide');
        }
    });
}

/** Initialise the performance time menu for select the graph's max days ago */
function initPerformanceTimeMenu() {
    for (const menuItem of el.performanceTimeMenuItems) {
        menuItem.addEventListener('click', async () => {
            if (
                menuItem.dataset.selected != undefined &&
                !el.performance.classList.contains('error')
            ) return;

            // Set as selected item
            for (const item of el.performanceTimeMenuItems) {
                if (item === menuItem) {
                    item.dataset.selected = '';
                } else {
                    delete item.dataset.selected;
                }
            }

            // Update Graph
            try {
                const factor = getSelectedFactor();
                const scores = await getFactorScores(
                    factor,
                    menuItem.dataset.maxDaysAgo
                );
                hidePerformanceError();
                updateScore(scores[0][factor]);
                updatePerformanceGraph(scores, factor);
            } catch (err) {
                showPerformanceError();
            }
        });
    }
}

/** Initialise Performance section */
async function initPerformance(worstBehaviour) {
    initPerformanceFactorMenu();
    initPerformanceTimeMenu();
    await setPerformanceFactor(worstBehaviour);
}


// Init
// ----------------------------------------------
/** Get the most latest/most recent scores  */
async function getLatestScores() {
    const response = await fetch('/api/scores?limit=1', {
        headers: {
            'Authorization': `Bearer ${accessToken}`,
        },
    });

    if (response.ok) {
        const scores = await response.json();
        return scores[0];
    } else {
        throw Error('Failed to fetch latest scores');
    }
}

/** Get page elements and store them in el */
function getElements() {
    el.main = document.querySelector('main');
    el.noDataMsg = document.querySelector('#no-data-msg');
    el.mainErrorMsg = document.querySelector('main > p.error');
    el.ecoDrivingScore = document.querySelector('#score-indicator');
    el.scoreValue = document.querySelector('#score-value');
    el.scoreImg = document.querySelector('#score-img');
    el.behavioursToImprove = document.querySelector('#behaviours-to-improve');
    el.journeysContainer = document.querySelector('#journeys-container');
    el.journeys = document.querySelector('#journeys');
    el.journeysTBody = el.journeys.querySelector('tbody');
    el.journeysLoadMore = document.querySelector('#journeys-load-more');
    el.performance = document.querySelector('#performance');
    el.performanceFactorName = document.querySelector('#performance-factor-name');
    el.performanceFactorNameH3 = el.performanceFactorName.querySelector('h3');
    el.performanceFactorNameIcon = el.performanceFactorName.querySelector('svg');
    el.performanceFactorDesc = document.querySelector('#performance-factor-desc');
    el.performanceFactorMenu = document.querySelector('#performance-factor-menu');
    el.performanceFactorMenuItemTmpl = document.querySelector('#performance-factor-menu-item-template');
    el.performanceFactorScore = document.querySelector('#performance-factor-score');
    el.performanceTimeMenuItems = document.querySelectorAll('#performance-time-menu > li');
    el.performanceGraph = document.querySelector('#performance-graph');
    el.performanceGraphCtx = el.performanceGraph.getContext('2d');
}

/** Show a notice indicating the user has no data and hide the body content */
function showNoDataMsg() {
    document.body.classList.add('showing-notice');
    el.noDataMsg.classList.remove('hide');
}

/** Show a fatal error, hiding the body content  */
function showFatalError() {
    document.body.classList.add('showing-notice');
    el.mainErrorMsg.classList.remove('hide');
}

async function init() {
    initCoreUI();
    getElements();
    accessToken = await authorize({ keepLoader: true });
    if (!accessToken) return;
    
    try {
        const latestScores = await getLatestScores();

        if (latestScores) {
            initEcoDrivingPerformance(latestScores.ecoDriving);
            const worstBehaviour = initBehavioursToImprove(latestScores);
            initJourneys();
            initPerformance(worstBehaviour);
        } else {
            showNoDataMsg();
        }
    } catch (err) {
        console.error(err);
        showFatalError();
    } finally {
        removeAuthLoader();
    }
}

window.addEventListener('load', init);
