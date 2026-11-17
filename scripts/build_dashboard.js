const fs = require('fs');
const path = require('path');

const playersData = [
  // BATTERS
  {
    rank: 1,
    role: 'Batter',
    id: 6288,
    name: 'Shubman Gill',
    team: 'India',
    countryCode: 'IND',
    isOverseas: false,
    score: 0.1401,
    pressureAbility: 0.4035,
    normalAbility: 0.1344,
    uplift: 0.2691,
    certainty: 92.6,
    balls: 204,
    matches: 18,
    totalBalls: 2804,
    archetype: 'Anchor-Elevator',
    cluster: 'Top Order Chasers',
    auctionPrice: 16.5,
    radar: [88, 92, 85, 93, 76, 82],
    scouting: 'Masterful anchor who elevates precisely when required run rate spikes. Exhibits exceptionally low dismissal hazard in high-leverage chases, controlling tempo through precise field manipulation.',
    phaseSplit: { powerplay: '+0.12', middle: '+0.18', death: '+0.27' },
    status: 'Retained Franchise Core'
  },
  {
    rank: 2,
    role: 'Batter',
    id: 6059,
    name: 'Ruturaj Gaikwad',
    team: 'India',
    countryCode: 'IND',
    isOverseas: false,
    score: 0.1394,
    pressureAbility: 0.3920,
    normalAbility: 0.0174,
    uplift: 0.3746,
    certainty: 98.6,
    balls: 250,
    matches: 16,
    totalBalls: 1889,
    archetype: 'Anchor-Elevator',
    cluster: 'Top Order Chasers',
    auctionPrice: 14.0,
    radar: [87, 90, 96, 99, 78, 65],
    scouting: 'Highest clutch uplift (+0.375) among top-order batters with 98.6% positive certainty. Dissects spin clamps and converts starts into match-winning targets under intense leverage.',
    phaseSplit: { powerplay: '+0.08', middle: '+0.22', death: '+0.38' },
    status: 'Franchise Captain / Spine'
  },
  {
    rank: 3,
    role: 'Batter',
    id: 1699,
    name: 'Suryakumar Yadav',
    team: 'India',
    countryCode: 'IND',
    isOverseas: false,
    score: 0.1318,
    pressureAbility: 0.3140,
    normalAbility: 0.2381,
    uplift: 0.0759,
    certainty: 72.6,
    balls: 533,
    matches: 46,
    totalBalls: 2850,
    archetype: '360° Enforcer',
    cluster: 'Death Finishers',
    auctionPrice: 18.0,
    radar: [85, 88, 70, 73, 94, 95],
    scouting: 'Absorbed 533 pressure deliveries across 46 matches. 360-degree boundary geometry manipulates defensive sweepers; scores at +0.314 runs/ball above par against frontline attacks.',
    phaseSplit: { powerplay: '+0.15', middle: '+0.28', death: '+0.34' },
    status: 'Marquee Match-Winner'
  },
  {
    rank: 4,
    role: 'Batter',
    id: 6396,
    name: 'Tim David',
    team: 'Australia',
    countryCode: 'AUS',
    isOverseas: true,
    score: 0.0738,
    pressureAbility: 0.2946,
    normalAbility: 0.2798,
    uplift: 0.0148,
    certainty: 56.0,
    balls: 439,
    matches: 44,
    totalBalls: 1293,
    archetype: 'Death Overs Finisher',
    cluster: 'Death Finishers',
    auctionPrice: 9.5,
    radar: [72, 85, 55, 56, 88, 97],
    scouting: 'Elite normal baseline (+0.280) allows him to clear boundaries against frontline pacers at death without warmup balls. Pure terminal power weapon for overs 17–20.',
    phaseSplit: { powerplay: '+0.00', middle: '+0.12', death: '+0.32' },
    status: 'Overseas Power Weapon'
  },
  {
    rank: 5,
    role: 'Batter',
    id: 5039,
    name: 'Rajat Patidar',
    team: 'India',
    countryCode: 'IND',
    isOverseas: false,
    score: 0.0312,
    pressureAbility: 0.2900,
    normalAbility: 0.1894,
    uplift: 0.1006,
    certainty: 73.6,
    balls: 249,
    matches: 20,
    totalBalls: 970,
    archetype: 'Spin Demolisher',
    cluster: 'Middle Order Enforcers',
    auctionPrice: 8.0,
    radar: [65, 84, 72, 74, 75, 85],
    scouting: 'Benchmark middle-overs aggressor (+0.101 uplift across 249 pressure balls). Dismantles opposition wrist-spin bottlenecks with decisive footwork and aerial range.',
    phaseSplit: { powerplay: '+0.05', middle: '+0.26', death: '+0.15' },
    status: 'Tactical Middle Core'
  },
  {
    rank: 6,
    role: 'Batter',
    id: 1318,
    name: 'Andre Russell',
    team: 'West Indies',
    countryCode: 'WI',
    isOverseas: true,
    score: 0.0172,
    pressureAbility: 0.2660,
    normalAbility: 0.0873,
    uplift: 0.1787,
    certainty: 90.0,
    balls: 363,
    matches: 30,
    totalBalls: 785,
    archetype: 'Impact Enforcer',
    cluster: 'Death Finishers',
    auctionPrice: 12.0,
    radar: [62, 80, 80, 90, 84, 74],
    scouting: '90.0% probability of positive uplift. Unmatched death overs boundary rate (24%+) in high-stakes finishes; turns 20-run equations on their head in 5 legal deliveries.',
    phaseSplit: { powerplay: '+0.00', middle: '+0.10', death: '+0.36' },
    status: 'Universal Match-Winner'
  },
  {
    rank: 7,
    role: 'Batter',
    id: 4117,
    name: 'Ishan Kishan',
    team: 'India',
    countryCode: 'IND',
    isOverseas: false,
    score: -0.0005,
    pressureAbility: 0.2160,
    normalAbility: 0.0068,
    uplift: 0.2092,
    certainty: 88.4,
    balls: 245,
    matches: 22,
    totalBalls: 2506,
    archetype: 'Powerplay Chaser',
    cluster: 'Top Order Chasers',
    auctionPrice: 10.5,
    radar: [55, 75, 82, 88, 77, 60],
    scouting: 'Massive personal clutch uplift (+0.209) with 88.4% certainty. Capitalizes ruthlessly on powerplay field restrictions during high-target chases; adds dual WK utility.',
    phaseSplit: { powerplay: '+0.25', middle: '+0.08', death: '+0.00' },
    status: 'Dynamic WK-Opener'
  },
  {
    rank: 8,
    role: 'Batter',
    id: 7897,
    name: 'Namboori Tilak Varma',
    team: 'India',
    countryCode: 'IND',
    isOverseas: false,
    score: -0.0044,
    pressureAbility: 0.1452,
    normalAbility: 0.0566,
    uplift: 0.0887,
    certainty: 81.8,
    balls: 745,
    matches: 54,
    totalBalls: 2631,
    archetype: 'High-Volume Anchor',
    cluster: 'Middle Order Enforcers',
    auctionPrice: 11.0,
    radar: [54, 68, 68, 82, 99, 70],
    scouting: 'Highest pressure sample depth in entire tournament (745 balls across 54 matches). Reliable squad spine who stabilizes collapses and anchors middle-overs resource preservation.',
    phaseSplit: { powerplay: '+0.06', middle: '+0.14', death: '+0.18' },
    status: 'Long-Term Core Anchor'
  },
  {
    rank: 9,
    role: 'Batter',
    id: 2639,
    name: 'Marcus Stoinis',
    team: 'Australia',
    countryCode: 'AUS',
    isOverseas: true,
    score: -0.0082,
    pressureAbility: 0.2224,
    normalAbility: 0.0248,
    uplift: 0.1975,
    certainty: 94.0,
    balls: 448,
    matches: 38,
    totalBalls: 1300,
    archetype: 'Heavy-Ball Finisher',
    cluster: 'Death Finishers',
    auctionPrice: 8.5,
    radar: [52, 76, 81, 94, 88, 66],
    scouting: '94.0% certainty of positive clutch uplift (+0.198). Power hitter against hostile pace at overs 17–20; muscle memory for clearing deep mid-wicket under pressure.',
    phaseSplit: { powerplay: '+0.02', middle: '+0.15', death: '+0.29' },
    status: 'Power Pace All-Rounder'
  },
  {
    rank: 10,
    role: 'Batter',
    id: 20702,
    name: 'Tristan Stubbs',
    team: 'South Africa',
    countryCode: 'SA',
    isOverseas: true,
    score: -0.0344,
    pressureAbility: 0.1894,
    normalAbility: 0.1003,
    uplift: 0.0892,
    certainty: 72.4,
    balls: 347,
    matches: 29,
    totalBalls: 1114,
    archetype: 'Dynamic 360° Finisher',
    cluster: 'Death Finishers',
    auctionPrice: 7.5,
    radar: [48, 72, 68, 72, 82, 77],
    scouting: 'Modern multi-angle death specialist. Excels against wide lines and reverse yorkers; agile boundary scavenger under high required run rates.',
    phaseSplit: { powerplay: '+0.00', middle: '+0.12', death: '+0.25' },
    status: 'Emerging Overseas Sensation'
  },

  // BOWLERS
  {
    rank: 1,
    role: 'Bowler',
    id: 2933,
    name: 'Jasprit Bumrah',
    team: 'India',
    countryCode: 'IND',
    isOverseas: false,
    score: 0.3510,
    pressureAbility: 0.5539,
    normalAbility: 0.1305,
    uplift: 0.4234,
    certainty: 100.0,
    balls: 404,
    matches: 35,
    totalBalls: 1780,
    archetype: 'Death Yorker Master',
    cluster: 'Death Closers',
    auctionPrice: 20.0,
    radar: [99, 100, 99, 100, 92, 82],
    scouting: 'Unrivaled world #1 (+0.351 conservative score, 100% certainty across 404 balls). Concedes under 6.0 RPO at the death with pinpoint yorkers, angled bouncers, and dipping off-cutters.',
    phaseSplit: { powerplay: '+0.20', middle: '+0.32', death: '+0.58' },
    status: 'Generational Benchmark'
  },
  {
    rank: 2,
    role: 'Bowler',
    id: 7920,
    name: 'Nathan Ellis',
    team: 'Australia',
    countryCode: 'AUS',
    isOverseas: true,
    score: 0.1363,
    pressureAbility: 0.3994,
    normalAbility: 0.1779,
    uplift: 0.2215,
    certainty: 88.4,
    balls: 223,
    matches: 21,
    totalBalls: 959,
    archetype: 'Skid Yorker Specialist',
    cluster: 'Death Closers',
    auctionPrice: 6.5,
    radar: [86, 91, 84, 88, 77, 86],
    scouting: 'Second highest conservative rating globally (+0.136). Low release trajectory creates skid off surface; executes wide-line yorkers with clinical repeatability.',
    phaseSplit: { powerplay: '+0.10', middle: '+0.18', death: '+0.42' },
    status: 'Prime RR Auction Target'
  },
  {
    rank: 3,
    role: 'Bowler',
    id: 7364,
    name: 'Haris Rauf',
    team: 'Pakistan',
    countryCode: 'PAK',
    isOverseas: true,
    score: 0.1240,
    pressureAbility: 0.3675,
    normalAbility: 0.0768,
    uplift: 0.2907,
    certainty: 95.2,
    balls: 276,
    matches: 23,
    totalBalls: 1063,
    archetype: 'Express Strike Enforcer',
    cluster: 'Express Strike',
    auctionPrice: 12.0,
    radar: [84, 89, 90, 95, 80, 72],
    scouting: '145–152 kph express velocity paired with heavy bouncers and dipping cutters (+0.291 uplift, 95.2% certainty). Breaks stubborn partnerships under tournament pressure.',
    phaseSplit: { powerplay: '+0.12', middle: '+0.25', death: '+0.40' },
    status: 'Global Benchmark Fast Bowler'
  },
  {
    rank: 4,
    role: 'Bowler',
    id: 781,
    name: 'Sunil Narine',
    team: 'West Indies',
    countryCode: 'WI',
    isOverseas: true,
    score: 0.0998,
    pressureAbility: 0.3452,
    normalAbility: 0.1653,
    uplift: 0.1799,
    certainty: 84.6,
    balls: 273,
    matches: 26,
    totalBalls: 1556,
    archetype: 'Mystery Spin Clamp',
    cluster: 'Middle Clamps',
    auctionPrice: 10.0,
    radar: [80, 87, 80, 85, 81, 85],
    scouting: 'Concealed revolutions with minimal trajectory deviation. Constricts middle overs to sub-6.2 RPO under pressure, forcing mistimed aerial boundary attempts.',
    phaseSplit: { powerplay: '+0.18', middle: '+0.35', death: '+0.12' },
    status: 'Middle-Overs Lockdown'
  },
  {
    rank: 5,
    role: 'Bowler',
    id: 2261,
    name: 'Harshal Patel',
    team: 'India',
    countryCode: 'IND',
    isOverseas: false,
    score: 0.0916,
    pressureAbility: 0.3039,
    normalAbility: -0.0480,
    uplift: 0.3520,
    certainty: 99.0,
    balls: 433,
    matches: 35,
    totalBalls: 1748,
    archetype: 'Deceptive Changeup Cutter',
    cluster: 'Changeup Cutters',
    auctionPrice: 9.0,
    radar: [78, 85, 95, 99, 91, 55],
    scouting: 'Huge +0.352 clutch uplift with 99.0% certainty across 433 balls. Master of dipping slower-ball off-cutters in overs 18–20; Purple Cap pedigree in high-stakes defense.',
    phaseSplit: { powerplay: '+0.00', middle: '+0.15', death: '+0.45' },
    status: 'Proven Domestic Death Spearhead'
  },
  {
    rank: 6,
    role: 'Bowler',
    id: 4900,
    name: 'Wanindu Hasaranga',
    team: 'Sri Lanka',
    countryCode: 'SL',
    isOverseas: true,
    score: 0.0797,
    pressureAbility: 0.2731,
    normalAbility: 0.0194,
    uplift: 0.2537,
    certainty: 96.8,
    balls: 429,
    matches: 39,
    totalBalls: 2054,
    archetype: 'Wrist Spin Match-Winner',
    cluster: 'Middle Clamps',
    auctionPrice: 8.5,
    radar: [76, 82, 88, 97, 90, 68],
    scouting: '96.8% positive uplift certainty across 429 balls. Traps middle-order batters with disguised googlies under pressure; turns dry overs into double-wicket breakthroughs.',
    phaseSplit: { powerplay: '+0.08', middle: '+0.34', death: '+0.10' },
    status: 'Prime RR Spin Target'
  },
  {
    rank: 7,
    role: 'Bowler',
    id: 8661,
    name: 'Matheesha Pathirana',
    team: 'Sri Lanka',
    countryCode: 'SL',
    isOverseas: true,
    score: 0.0557,
    pressureAbility: 0.2745,
    normalAbility: 0.1350,
    uplift: 0.1395,
    certainty: 82.2,
    balls: 400,
    matches: 24,
    totalBalls: 1279,
    archetype: 'Sling Death Disruptor',
    cluster: 'Death Closers',
    auctionPrice: 11.0,
    radar: [70, 82, 75, 82, 88, 83],
    scouting: 'Malinga-like sling trajectory with extreme tailing in. Concedes 2.4 runs/over below phase par in overs 18–20 across 400 pressure balls; unpickable slower balls under lights.',
    phaseSplit: { powerplay: '+0.00', middle: '+0.14', death: '+0.48' },
    status: 'Marquee Death Closer Target'
  },
  {
    rank: 8,
    role: 'Bowler',
    id: 3644,
    name: 'Kuldeep Yadav',
    team: 'India',
    countryCode: 'IND',
    isOverseas: false,
    score: 0.0128,
    pressureAbility: 0.2198,
    normalAbility: 0.0443,
    uplift: 0.1755,
    certainty: 89.0,
    balls: 404,
    matches: 40,
    totalBalls: 1965,
    archetype: 'Left-Arm Wrist Spinner',
    cluster: 'Middle Clamps',
    auctionPrice: 10.0,
    radar: [60, 76, 78, 89, 89, 72],
    scouting: '89.0% certainty of positive uplift across 404 balls. Attacks stumps with drift and sharp turn in middle squeeze; forces mis-hits on good balls under RRR pressure.',
    phaseSplit: { powerplay: '+0.05', middle: '+0.28', death: '+0.05' },
    status: 'Domestic Spin Pillar'
  },
  {
    rank: 9,
    role: 'Bowler',
    id: 360,
    name: 'Bhuvneshwar Kumar',
    team: 'India',
    countryCode: 'IND',
    isOverseas: false,
    score: 0.0121,
    pressureAbility: 0.2061,
    normalAbility: 0.0473,
    uplift: 0.1587,
    certainty: 87.6,
    balls: 374,
    matches: 40,
    totalBalls: 2314,
    archetype: 'Swing & Seam Precision',
    cluster: 'Changeup Cutters',
    auctionPrice: 6.0,
    radar: [59, 75, 77, 88, 88, 73],
    scouting: '87.6% certainty across 374 deliveries. Veteran accuracy in powerplay and penultimate overs; master of wide yorkers and knuckle balls under high leverage.',
    phaseSplit: { powerplay: '+0.22', middle: '+0.10', death: '+0.20' },
    status: 'High-Value Tactical Asset'
  },
  {
    rank: 10,
    role: 'Bowler',
    id: 4373,
    name: 'Mustafizur Rahman',
    team: 'Bangladesh',
    countryCode: 'BAN',
    isOverseas: true,
    score: -0.0069,
    pressureAbility: 0.2067,
    normalAbility: 0.0709,
    uplift: 0.1358,
    certainty: 85.8,
    balls: 499,
    matches: 41,
    totalBalls: 1646,
    archetype: 'Left-Arm Cutter Artist',
    cluster: 'Express Strike',
    auctionPrice: 5.5,
    radar: [53, 75, 74, 86, 93, 75],
    scouting: 'Absorbed 499 pressure deliveries across 41 matches with 85.8% certainty. Heavy off-cutters bite off the surface, eliminating boundary options for pull shots.',
    phaseSplit: { powerplay: '+0.10', middle: '+0.12', death: '+0.30' },
    status: 'Tactical Cutters Option'
  }
];

const dashboardHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rajasthan Royals | SupeRR Selector Season 2 — Executive Pressure Analytics</title>
  
  <!-- Chart.js for data visualization -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
  
  <style>
    /* Design Tokens: Restrained Institutional Palette */
    :root {
      --rr-navy: #001D48;
      --rr-navy-deep: #00122E;
      --rr-navy-subtle: #EBF1F7;
      --rr-pink: #C2005B;
      --rr-pink-subtle: #FDF2F7;
      --ink-primary: #111827;
      --ink-secondary: #374151;
      --ink-muted: #6B7280;
      --surface-canvas: #F8F9FA;
      --surface-panel: #FFFFFF;
      --border-light: #E5E7EB;
      --border-strong: #D1D5DB;
      --signal-green: #047857;
      --signal-green-bg: #ECFDF5;
      --signal-red: #B91C1C;
      --signal-red-bg: #FEF2F2;
      --signal-amber: #B45309;
      --signal-amber-bg: #FFFBEB;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 14px;
      line-height: 1.5;
      color: var(--ink-secondary);
      background-color: var(--surface-canvas);
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    /* Type Scale: Obvious steps >= 1.25x ratio */
    h1 {
      font-size: 26px;
      line-height: 1.2;
      font-weight: 700;
      color: var(--rr-navy);
      letter-spacing: -0.025em;
    }

    h2 {
      font-size: 20px;
      line-height: 1.3;
      font-weight: 600;
      color: var(--ink-primary);
      letter-spacing: -0.015em;
      margin-bottom: 4px;
    }

    h3 {
      font-size: 15px;
      line-height: 1.4;
      font-weight: 600;
      color: var(--ink-primary);
    }

    .tabular-nums {
      font-variant-numeric: tabular-nums;
      font-feature-settings: "tnum" 1;
    }

    /* Top Masthead */
    .masthead {
      background: var(--surface-panel);
      border-bottom: 1px solid var(--border-light);
      padding: 16px 32px;
    }

    .masthead-inner {
      max-width: 1520px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 24px;
      flex-wrap: wrap;
    }

    .org-identity {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .org-badge {
      width: 44px;
      height: 44px;
      background: var(--rr-navy);
      color: #FFFFFF;
      font-weight: 900;
      font-size: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 4px;
      flex-shrink: 0;
      letter-spacing: -0.05em;
    }

    .org-meta {
      font-size: 12px;
      color: var(--ink-muted);
      margin-top: 2px;
    }

    .masthead-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
      text-decoration: none;
      border: 1px solid var(--border-strong);
      background: var(--surface-panel);
      color: var(--ink-secondary);
    }

    .btn:hover {
      background: var(--surface-canvas);
      border-color: var(--ink-secondary);
      color: var(--ink-primary);
    }

    .btn:focus-visible {
      outline: 2px solid var(--rr-pink);
      outline-offset: 1px;
    }

    .btn-primary {
      background: var(--rr-navy);
      border-color: var(--rr-navy);
      color: #FFFFFF;
    }

    .btn-primary:hover {
      background: var(--rr-navy-deep);
      border-color: var(--rr-navy-deep);
      color: #FFFFFF;
    }

    /* Flat Metric Ribbon (Ticker) */
    .metric-strip {
      background: var(--surface-panel);
      border-bottom: 1px solid var(--border-light);
      padding: 14px 0;
    }

    .metric-strip-inner {
      max-width: 1520px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      padding: 0 32px;
    }

    .strip-item {
      padding: 12px 16px;
      border-right: 1px solid var(--border-light);
    }

    .strip-item:first-child {
      padding-left: 0;
    }

    .strip-item:last-child {
      border-right: none;
      padding-right: 0;
    }

    .strip-label {
      font-size: 12px;
      font-weight: 500;
      color: var(--ink-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .strip-value {
      font-size: 15px;
      font-weight: 700;
      color: var(--ink-primary);
      margin-top: 2px;
    }

    .strip-sub {
      font-size: 12px;
      color: var(--ink-muted);
    }

    /* Navigation Tabs */
    .nav-bar {
      background: var(--surface-panel);
      border-bottom: 1px solid var(--border-strong);
    }

    .nav-inner {
      max-width: 1520px;
      margin: 0 auto;
      display: flex;
      gap: 24px;
      padding: 0 32px;
      overflow-x: auto;
    }

    .nav-tab {
      background: none;
      border: none;
      border-bottom: 2px solid transparent;
      padding: 12px 0;
      font-size: 13px;
      font-weight: 500;
      color: var(--ink-muted);
      cursor: pointer;
      white-space: nowrap;
      transition: color 0.15s ease, border-color 0.15s ease;
    }

    .nav-tab:hover {
      color: var(--ink-primary);
    }

    .nav-tab.active {
      color: var(--rr-navy);
      font-weight: 600;
      border-bottom-color: var(--rr-pink);
    }

    .nav-tab:focus-visible {
      outline: 2px solid var(--rr-pink);
      outline-offset: -2px;
    }

    /* Main Content Layout */
    .app-main {
      max-width: 1520px;
      margin: 0 auto;
      padding: 24px 32px;
      width: 100%;
    }

    /* Filter Toolbar (Flat Row) */
    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }

    .filter-group {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .search-box {
      position: relative;
      min-width: 260px;
    }

    .search-input {
      width: 100%;
      padding: 6px 12px 6px 30px;
      border: 1px solid var(--border-strong);
      border-radius: 4px;
      font-size: 12px;
      color: var(--ink-primary);
      background: var(--surface-panel);
    }

    .search-input:focus {
      outline: none;
      border-color: var(--rr-navy);
      box-shadow: 0 0 0 1px var(--rr-navy);
    }

    .search-icon {
      position: absolute;
      left: 10px;
      top: 50%;
      transform: translateY(-50%);
      width: 13px;
      height: 13px;
      stroke: var(--ink-muted);
    }

    .segmented-control {
      display: inline-flex;
      border: 1px solid var(--border-strong);
      border-radius: 4px;
      background: var(--surface-panel);
      padding: 2px;
    }

    .segment-btn {
      background: none;
      border: none;
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 500;
      color: var(--ink-muted);
      cursor: pointer;
      border-radius: 2px;
      transition: background 0.15s ease, color 0.15s ease;
    }

    .segment-btn.active {
      background: var(--rr-navy);
      color: #FFFFFF;
    }

    /* Data Tables: Professional, Dense, High-Contrast */
    .data-table-wrapper {
      background: transparent;
      border: none;
      overflow-x: auto;
      margin-bottom: 16px;
    }

    .data-table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      text-align: left;
      background: var(--surface-panel);
      border: 1px solid var(--border-strong);
      border-radius: 4px;
    }

    .data-table th {
      padding: 12px 16px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--ink-muted);
      background: var(--surface-canvas);
      border-bottom: 1px solid var(--border-strong);
      white-space: nowrap;
      user-select: none;
      cursor: pointer;
    }

    .data-table th:hover {
      color: var(--ink-primary);
    }

    .data-table td {
      padding: 12px 16px;
      font-size: 13px;
      color: var(--ink-secondary);
      border-bottom: 1px solid var(--border-light);
      white-space: nowrap;
    }

    .data-table tr:last-child td {
      border-bottom: none;
    }

    .data-table tr:hover td {
      background-color: #F8FAFC;
    }

    .data-table tr.active-row td {
      background-color: var(--rr-navy-subtle);
    }

    .country-pill {
      display: inline-block;
      padding: 2px 8px;
      border: 1px solid var(--border-strong);
      border-radius: 3px;
      font-size: 12px;
      font-weight: 600;
      color: var(--ink-secondary);
      background: var(--surface-canvas);
      letter-spacing: 0.04em;
    }

    .rank-number {
      font-weight: 700;
      color: var(--ink-primary);
    }

    .rank-number.top-rank {
      color: var(--rr-pink);
    }

    .player-name {
      font-weight: 600;
      color: var(--ink-primary);
    }

    .stat-positive {
      color: var(--signal-green);
      font-weight: 600;
    }

    .stat-negative {
      color: var(--signal-red);
      font-weight: 600;
    }

    /* Master-Detail Split Screen Layout */
    .workbench-layout {
      display: grid;
      grid-template-columns: 1fr 400px;
      gap: 24px;
      align-items: start;
    }

    .workbench-layout.detail-hidden {
      grid-template-columns: 1fr;
    }

    /* Detail Dossier Panel */
    .dossier-panel {
      background: var(--surface-panel);
      border: 1px solid var(--border-strong);
      border-radius: 4px;
      padding: 20px;
      position: sticky;
      top: 24px;
    }

    .dossier-header {
      border-bottom: 1px solid var(--border-light);
      padding-bottom: 14px;
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }

    .dossier-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      margin-bottom: 16px;
    }

    .dossier-stat-box {
      border: 1px solid var(--border-light);
      padding: 8px 12px;
      border-radius: 4px;
      background: var(--surface-canvas);
    }

    .dossier-stat-label {
      font-size: 12px;
      color: var(--ink-muted);
      text-transform: uppercase;
      font-weight: 500;
    }

    .dossier-stat-value {
      font-size: 16px;
      font-weight: 700;
      color: var(--ink-primary);
      margin-top: 2px;
    }

    /* Chart Containers */
    .chart-panel {
      background: var(--surface-panel);
      border: 1px solid var(--border-strong);
      border-radius: 4px;
      padding: 20px;
      margin-bottom: 24px;
    }

    .chart-header {
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      border-bottom: 1px solid var(--border-light);
      padding-bottom: 10px;
    }

    .chart-canvas-container {
      position: relative;
      height: 400px;
      width: 100%;
    }

    /* Two Column Comparative Layout */
    .compare-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-top: 16px;
    }

    /* Tabular Form / Input Sheet */
    .sheet-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 0;
      border-bottom: 1px solid var(--border-light);
      font-size: 13px;
    }

    .sheet-row:last-child {
      border-bottom: none;
    }

    /* Toast Notification (Honest, Unobtrusive) */
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--rr-navy);
      color: #FFFFFF;
      padding: 10px 16px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 100;
      transition: opacity 0.2s ease, transform 0.2s ease;
    }

    /* Responsive adjustments */
    @media (max-width: 1180px) {
      .metric-strip-inner { grid-template-columns: repeat(2, 1fr); }
      .strip-item:nth-child(2) { border-right: none; }
      .workbench-layout { grid-template-columns: 1fr; }
      .dossier-panel { position: static; }
    }

    @media (max-width: 768px) {
      .masthead, .app-main, .nav-inner, .metric-strip-inner { padding-left: 16px; padding-right: 16px; }
      .metric-strip-inner { grid-template-columns: 1fr; }
      .strip-item { border-right: none; border-bottom: 1px solid var(--border-light); padding: 8px 0; }
      .compare-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

  <!-- Masthead -->
  <header class="masthead">
    <div class="masthead-inner">
      <div class="org-identity">
        <div class="org-badge">RR</div>
        <div>
          <h1>Rajasthan Royals Analytics & Strategy Group</h1>
          <h2 class="org-meta" style="font-size: 13px; font-weight: 500; color: var(--ink-muted); margin-top: 2px;">
            SupeRR Selector Season 2 • High-Leverage Pressure Reliability Platform • Prepared for Kumar Sangakkara & Giles Lindsay
          </h2>
        </div>
      </div>

      <div class="masthead-actions">
        <button onclick="exportCSV()" class="btn">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Export CSV
        </button>
        <button onclick="exportJSON()" class="btn">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          Export JSON
        </button>
        <button onclick="window.print()" class="btn btn-primary">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
          Print Briefing
        </button>
      </div>
    </div>
  </header>

  <!-- Metric Strip (Audited Financial Style) -->
  <div class="metric-strip">
    <div class="metric-strip-inner tabular-nums">
      <div class="strip-item">
        <div class="strip-label">Canonical Dataset</div>
        <div class="strip-value">200,999 Deliveries</div>
        <div class="strip-sub">867 IPL & T20I Matches (2022–2026)</div>
      </div>
      <div class="strip-item">
        <div class="strip-label">High-Leverage Cutoff (L &ge; Q0.80)</div>
        <div class="strip-value">39,747 Deliveries</div>
        <div class="strip-sub">Top 20% Outcome Urgency & Swing</div>
      </div>
      <div class="strip-item">
        <div class="strip-label">Batters Holdout Validity</div>
        <div class="strip-value stat-positive">1.3688 RMSE (-19.3%)</div>
        <div class="strip-sub">Vs Base 1.6965 &bull; Pearson r = 0.640</div>
      </div>
      <div class="strip-item">
        <div class="strip-label">Bowlers Holdout Validity</div>
        <div class="strip-value stat-positive">0.9131 RMSE (-15.1%)</div>
        <div class="strip-sub">Vs Base 1.0757 &bull; Pearson r = 0.643</div>
      </div>
      <div class="strip-item">
        <div class="strip-label">Unstop Platform Audit</div>
        <div class="strip-value">20 / 20 Verified</div>
        <div class="strip-sub">0 Duplicates &bull; Exact Dropdown Match</div>
      </div>
    </div>
  </div>

  <!-- Operational Navigation Tabs -->
  <nav class="nav-bar" role="tablist">
    <div class="nav-inner">
      <button onclick="switchTab('roster')" id="tab-roster" role="tab" aria-selected="true" class="nav-tab active">
        Roster Evaluation Matrix
      </button>
      <button onclick="switchTab('quadrant')" id="tab-quadrant" role="tab" aria-selected="false" class="nav-tab">
        Bivariate Performance Map
      </button>
      <button onclick="switchTab('comparator')" id="tab-comparator" role="tab" aria-selected="false" class="nav-tab">
        Pairwise Scouting Dossier
      </button>
      <button onclick="switchTab('ledger')" id="tab-ledger" role="tab" aria-selected="false" class="nav-tab">
        Auction Allocation Ledger
      </button>
      <button onclick="switchTab('proof')" id="tab-proof" role="tab" aria-selected="false" class="nav-tab">
        Methodology & Empirical Proof
      </button>
    </div>
  </nav>

  <!-- Main Content Area -->
  <main class="app-main">

    <!-- ======================================================== -->
    <!-- TAB 1: ROSTER EVALUATION MATRIX -->
    <!-- ======================================================== -->
    <div id="view-roster">
      <h2 style="font-size: 18px; font-weight: 600; color: var(--ink-primary); margin-bottom: 16px;">Roster Evaluation Matrix & Player Dossier</h2>
      <div class="toolbar">
        <div class="filter-group">
          <!-- Search -->
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input type="text" id="searchInput" placeholder="Filter by player, team, or role..." class="search-input" oninput="applyFilters()">
          </div>

          <!-- Discipline -->
          <div class="segmented-control" role="group" aria-label="Discipline Filter">
            <button onclick="setDiscipline('all')" id="btn-disc-all" class="segment-btn active">All Players (20)</button>
            <button onclick="setDiscipline('Batter')" id="btn-disc-bat" class="segment-btn">Batters (10)</button>
            <button onclick="setDiscipline('Bowler')" id="btn-disc-bowl" class="segment-btn">Bowlers (10)</button>
          </div>

          <!-- Nationality -->
          <div class="segmented-control" role="group" aria-label="Nationality Filter">
            <button onclick="setNationality('all')" id="btn-nat-all" class="segment-btn active">Global</button>
            <button onclick="setNationality('domestic')" id="btn-nat-dom" class="segment-btn">India</button>
            <button onclick="setNationality('overseas')" id="btn-nat-ovs" class="segment-btn">Overseas</button>
          </div>
        </div>

        <div style="font-size: 12px; color: var(--ink-muted);" class="tabular-nums">
          Showing <strong id="recordCount" style="color: var(--ink-primary);">20</strong> verified players
        </div>
      </div>

      <!-- Master-Detail Layout -->
      <div id="workbenchContainer" class="workbench-layout">
        <!-- Table (Master) -->
        <div class="data-table-wrapper">
          <table class="data-table tabular-nums">
            <thead>
              <tr>
                <th onclick="sortTable('rank')">Rank</th>
                <th onclick="sortTable('name')">Player</th>
                <th onclick="sortTable('role')">Role</th>
                <th onclick="sortTable('team')">Nation</th>
                <th onclick="sortTable('score')" style="text-align: right;">Score (Q0.10)</th>
                <th onclick="sortTable('pressureAbility')" style="text-align: right;">Pressure &mu;</th>
                <th onclick="sortTable('normalAbility')" style="text-align: right;">Normal Par &mu;</th>
                <th onclick="sortTable('uplift')" style="text-align: right;">Uplift &Delta;</th>
                <th onclick="sortTable('certainty')" style="text-align: right;">P(&Delta; &gt; 0)</th>
                <th onclick="sortTable('balls')" style="text-align: right;">Balls</th>
                <th onclick="sortTable('matches')" style="text-align: right;">Matches</th>
              </tr>
            </thead>
            <tbody id="rosterTableBody">
              <!-- Dynamically populated rows -->
            </tbody>
          </table>
        </div>

        <!-- Detail Dossier Panel -->
        <aside id="dossierPanel" class="dossier-panel">
          <div class="dossier-header">
            <div>
              <div id="dossierRole" style="font-size: 12px; text-transform: uppercase; font-weight: 600; color: var(--ink-muted);">Role</div>
              <h3 id="dossierName" style="font-size: 18px; margin-top: 2px;">Player Name</h3>
              <div id="dossierTeam" style="font-size: 12px; color: var(--ink-muted); margin-top: 2px;">Nation &bull; ID: 0000</div>
            </div>
            <button onclick="closeDossier()" class="btn" style="padding: 4px 10px; font-size: 12px;">Close</button>
          </div>

          <div class="dossier-grid tabular-nums">
            <div class="dossier-stat-box">
              <div class="dossier-stat-label">Conservative Q0.10</div>
              <div id="dossierScore" class="dossier-stat-value" style="color: var(--rr-pink);">+0.000</div>
            </div>
            <div class="dossier-stat-box">
              <div class="dossier-stat-label">Clutch Uplift &Delta;</div>
              <div id="dossierUplift" class="dossier-stat-value stat-positive">+0.000</div>
            </div>
            <div class="dossier-stat-box">
              <div class="dossier-stat-label">Pressure Ability</div>
              <div id="dossierPress" class="dossier-stat-value">+0.000</div>
            </div>
            <div class="dossier-stat-box">
              <div class="dossier-stat-label">Posterior Certainty</div>
              <div id="dossierCertainty" class="dossier-stat-value">0.0%</div>
            </div>
          </div>

          <!-- Mathematical Distribution Curve -->
          <div style="margin-bottom: 16px;">
            <div style="font-size: 12px; text-transform: uppercase; font-weight: 600; color: var(--ink-muted); margin-bottom: 6px;">
              Empirical Bayes Posterior Distribution
            </div>
            <div style="border: 1px solid var(--border-light); border-radius: 4px; padding: 10px; background: var(--surface-canvas);">
              <canvas id="posteriorCanvas" width="360" height="120" style="width: 100%; height: 120px;"></canvas>
            </div>
            <div style="font-size: 12px; color: var(--ink-muted); margin-top: 4px;">
              Dashed line marks conservative 10th percentile cutoff (<span style="color: var(--rr-pink); font-weight: 600;">Q0.10</span>).
            </div>
          </div>

          <!-- Tactical Scouting Note -->
          <div style="margin-bottom: 16px;">
            <div style="font-size: 12px; text-transform: uppercase; font-weight: 600; color: var(--ink-muted); margin-bottom: 6px;">
              War Room Technical Evaluation
            </div>
            <p id="dossierScouting" style="font-size: 12px; line-height: 1.55; color: var(--ink-secondary);">
              Scouting profile text.
            </p>
          </div>

          <button id="dossierDraftBtn" onclick="togglePlayerFromDossier()" class="btn btn-primary" style="width: 100%; justify-content: center;">
            Add to Auction Allocation Ledger
          </button>
        </aside>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- TAB 2: BIVARIATE PERFORMANCE MAP -->
    <!-- ======================================================== -->
    <div id="view-quadrant" style="display: none;">
      <div class="chart-panel">
        <div class="chart-header">
          <div>
            <h2>Bivariate Performance Map: Pressure Ability vs. Normal Baseline</h2>
            <p style="font-size: 12px; color: var(--ink-muted); margin-top: 2px;">
              Bubble diameter proportional to high-leverage deliveries. Coordinates isolate repeatable executioners from unadjusted volume aggregators.
            </p>
          </div>
          <div style="font-size: 12px; color: var(--ink-muted); display: flex; gap: 16px;">
            <span style="display: inline-flex; align-items: center; gap: 6px;">
              <span style="width: 10px; height: 10px; background: var(--rr-pink); border-radius: 50%;"></span> Batters
            </span>
            <span style="display: inline-flex; align-items: center; gap: 6px;">
              <span style="width: 10px; height: 10px; background: var(--rr-navy); border-radius: 50%;"></span> Bowlers
            </span>
          </div>
        </div>

        <div class="chart-canvas-container">
          <canvas id="bivariateChart"></canvas>
        </div>
      </div>

      <!-- Quadrant Breakdown Table -->
      <div class="data-table-wrapper" style="margin-top: 24px;">
        <table class="data-table">
          <thead>
            <tr>
              <th>Quadrant Classification</th>
              <th>Mathematical Boundary</th>
              <th>Primary Exemplars</th>
              <th>Tactical Deployment Directive</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="font-weight: 600; color: var(--signal-green);">Elite Clutch Match-Winners</td>
              <td class="tabular-nums">&mu;_press &gt; 0.25, &mu;_norm &gt; 0.10</td>
              <td>Jasprit Bumrah, Shubman Gill, Suryakumar Yadav, Nathan Ellis</td>
              <td>Lock down as primary match closers and high-leverage run-chase anchors.</td>
            </tr>
            <tr>
              <td style="font-weight: 600; color: var(--rr-pink);">Pure Clutch Elevators</td>
              <td class="tabular-nums">&mu;_press &gt; 0.25, &mu;_norm &le; 0.10</td>
              <td>Ruturaj Gaikwad, Harshal Patel, Haris Rauf</td>
              <td>Deploy specifically when required run rate spikes or during death overs defense.</td>
            </tr>
            <tr>
              <td style="font-weight: 600; color: var(--ink-secondary);">High Baseline Enforcers</td>
              <td class="tabular-nums">&mu;_press &le; 0.25, &mu;_norm &gt; 0.10</td>
              <td>Tim David, Tristan Stubbs, Rajat Patidar</td>
              <td>Maintain high ceiling through sheer boundary hitting power; manage dismissal exposure.</td>
            </tr>
            <tr>
              <td style="font-weight: 600; color: var(--signal-red);">High-Variance Volume Anchors</td>
              <td class="tabular-nums">&mu;_press &le; 0.25, &mu;_norm &le; 0.10</td>
              <td>Namboori Tilak Varma, Mustafizur Rahman</td>
              <td>Absorb volume during middle-overs resource preservation; avoid paying marquee auction premiums.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- TAB 3: PAIRWISE SCOUTING DOSSIER -->
    <!-- ======================================================== -->
    <div id="view-comparator" style="display: none;">
      <h2 style="font-size: 18px; font-weight: 600; color: var(--ink-primary); margin-bottom: 16px;">Pairwise Scouting Comparison Dossier</h2>
      <div class="toolbar" style="margin-bottom: 24px;">
        <div class="filter-group">
          <label for="compareSelectA" style="font-size: 12px; font-weight: 600; color: var(--ink-primary);">Player A:</label>
          <select id="compareSelectA" class="btn" style="padding: 6px 10px;" onchange="renderComparison()"></select>
          
          <span style="font-size: 12px; color: var(--ink-muted); margin: 0 8px;">vs.</span>

          <label for="compareSelectB" style="font-size: 12px; font-weight: 600; color: var(--ink-primary);">Player B:</label>
          <select id="compareSelectB" class="btn" style="padding: 6px 10px;" onchange="renderComparison()"></select>
        </div>

        <div style="display: flex; gap: 8px;">
          <button onclick="loadComparisonPreset(6288, 6059)" class="btn">Gill vs. Gaikwad</button>
          <button onclick="loadComparisonPreset(2933, 7920)" class="btn">Bumrah vs. Ellis</button>
          <button onclick="loadComparisonPreset(1318, 6396)" class="btn">Russell vs. David</button>
        </div>
      </div>

      <div class="compare-grid tabular-nums">
        <!-- Player A Column -->
        <div id="compareCardA" class="chart-panel" style="margin-bottom: 0;">
          <!-- Populated dynamically -->
        </div>

        <!-- Player B Column -->
        <div id="compareCardB" class="chart-panel" style="margin-bottom: 0;">
          <!-- Populated dynamically -->
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- TAB 4: AUCTION ALLOCATION LEDGER -->
    <!-- ======================================================== -->
    <div id="view-ledger" style="display: none;">
      <div class="chart-panel">
        <div class="chart-header">
          <div>
            <h2>Rajasthan Royals Clutch Spine (6 Core Roles)</h2>
            <p style="font-size: 12px; color: var(--ink-muted); margin-top: 2px;">
              Simulate auction target allocations adhering strictly to BCCI regulations (Max 4 Overseas in Playing XI).
            </p>
          </div>
          <div style="display: flex; gap: 8px;">
            <button onclick="loadLedgerPreset('fortress')" class="btn">Preset: Fortress Defense</button>
            <button onclick="loadLedgerPreset('power')" class="btn">Preset: Power Chase</button>
            <button onclick="loadLedgerPreset('domestic')" class="btn">Preset: Indian Core</button>
            <button onclick="clearLedger()" class="btn">Reset</button>
          </div>
        </div>

        <!-- Ledger Summary Strip -->
        <div class="metric-strip" style="border: 1px solid var(--border-light); border-radius: 4px; margin-bottom: 20px; padding: 14px 0;">
          <div class="metric-strip-inner tabular-nums" style="grid-template-columns: repeat(4, 1fr); padding: 0 16px;">
            <div class="strip-item">
              <div class="strip-label">Slots Filled</div>
              <div id="ledgerFilledCount" class="strip-value">0 / 6</div>
            </div>
            <div class="strip-item">
              <div class="strip-label">Overseas Quota Status</div>
              <div id="ledgerOverseasCount" class="strip-value">0 / 4 Overseas</div>
            </div>
            <div class="strip-item">
              <div class="strip-label">Committed Cap Allocation</div>
              <div id="ledgerBudgetSum" class="strip-value">&pound; 0.0 Cr</div>
            </div>
            <div class="strip-item">
              <div class="strip-label">Cumulative Reliability Floor</div>
              <div id="ledgerScoreSum" class="strip-value stat-positive">+0.000</div>
            </div>
          </div>
        </div>

        <!-- Allocation Table -->
        <div class="data-table-wrapper">
          <table class="data-table tabular-nums">
            <thead>
              <tr>
                <th>Tactical Role Slot</th>
                <th>Target Player</th>
                <th>Nation</th>
                <th>Discipline</th>
                <th style="text-align: right;">Floor (Q0.10)</th>
                <th style="text-align: right;">Uplift &Delta;</th>
                <th style="text-align: right;">Estimated Cap</th>
                <th style="text-align: center;">Action</th>
              </tr>
            </thead>
            <tbody id="ledgerTableBody">
              <!-- Dynamically rendered slots -->
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- TAB 5: METHODOLOGY & EMPIRICAL PROOF -->
    <!-- ======================================================== -->
    <div id="view-proof" style="display: none;">
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
        
        <!-- Out-of-sample chart -->
        <div class="chart-panel">
          <div class="chart-header">
            <div>
              <h2>Out-of-Sample Holdout Verification</h2>
              <p style="font-size: 12px; color: var(--ink-muted); margin-top: 2px;">
                Tested on 174 untouched matches across 517 held-out test players with zero data leakage.
              </p>
            </div>
          </div>
          <div class="chart-canvas-container" style="height: 300px;">
            <canvas id="holdoutChart"></canvas>
          </div>
        </div>

        <!-- Jackknife & Bayesian Rigor -->
        <div class="chart-panel">
          <div class="chart-header">
            <div>
              <h3 style="font-size: 15px; font-weight: 600; color: var(--ink-primary);">Sensitivity & Quantile Regularization</h3>
              <p style="font-size: 12px; color: var(--ink-muted); margin-top: 2px;">
                Guarantees rankings cannot be distorted by single-innings heroics or small-sample noise.
              </p>
            </div>
          </div>

          <div style="display: flex; flex-direction: column; gap: 16px; margin-top: 12px;">
            <div class="sheet-row">
              <div>
                <strong>Jackknife Match Exclusion Test</strong>
                <div style="font-size: 12px; color: var(--ink-muted);">Dropping each player's highest scoring match preserves &ge; 80% of leaderboard.</div>
              </div>
              <span class="country-pill" style="color: var(--signal-green); font-weight: 700;">&ge; 80.0% STABLE</span>
            </div>

            <div class="sheet-row">
              <div>
                <strong>Conservative Quantile Ranking (Q0.10)</strong>
                <div style="font-size: 12px; color: var(--ink-muted);">Score = &mu; - 1.282&sigma; penalizes limited sample size and high posterior variance.</div>
              </div>
              <span class="country-pill" style="color: var(--rr-navy); font-weight: 700;">90% CREDIBLE</span>
            </div>

            <div class="sheet-row">
              <div>
                <strong>Unstop Dropdown Integrity Verification</strong>
                <div style="font-size: 12px; color: var(--ink-muted);">Zero duplicate IDs. Exact 1-to-1 match against official tournament rosters.</div>
              </div>
              <span class="country-pill" style="color: var(--signal-green); font-weight: 700;">20 / 20 PASS</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Formal Mathematical Architecture -->
      <div class="data-table-wrapper" style="margin-top: 24px;">
        <table class="data-table">
          <thead>
            <tr>
              <th>Pipeline Stage</th>
              <th>Mathematical Formulation</th>
              <th>Statistical Mechanism</th>
              <th>Operational Function</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="font-weight: 600; color: var(--rr-navy);">1. Match Context Baselines</td>
              <td style="font-family: ui-monospace, monospace; font-size: 12px;">E[Runs | BallsRem, WktsRem, CRR, RRR, Phase, Venue]</td>
              <td>Gradient-boosted situation trees with out-of-fold cross-validation.</td>
              <td>Conditions par continuously on game state rather than static phase averages.</td>
            </tr>
            <tr>
              <td style="font-weight: 600; color: var(--rr-navy);">2. Leverage Volatility Spread</td>
              <td style="font-family: ui-monospace, monospace; font-size: 12px;">L(s) = sqrt(&Sigma; P(o)[p(s_o) - p_bar(s)]^2) &times; urgency</td>
              <td>Dynamic outcome win probability variance across legal transitions.</td>
              <td>Top 20% quantile (L &ge; Q0.80) strictly isolates genuine high-pressure deliveries.</td>
            </tr>
            <tr>
              <td style="font-weight: 600; color: var(--rr-navy);">3. Run-Equivalent Valuation</td>
              <td style="font-family: ui-monospace, monospace; font-size: 12px;">V_bat = r_runs + c(s)&middot;r_surv &bull; V_bowl = r_econ + c(s)&middot;r_wkts</td>
              <td>Dynamic wicket pricing c(s) scaled from 6.0 runs (PP) to 12.0 runs (Death).</td>
              <td>Synthesizes boundary hitting, dot suppression, and wickets into unified currency.</td>
            </tr>
            <tr>
              <td style="font-weight: 600; color: var(--rr-navy);">4. Empirical Bayes Calibration</td>
              <td style="font-family: ui-monospace, monospace; font-size: 12px;">Score = Q0.10(Posterior) = &mu;_i - 1.282&middot;&sigma;_i</td>
              <td>Hierarchical partial pooling decomposes player skill into baseline &amp; clutch shift.</td>
              <td>Enforces conservative 90% statistical lower bound to eliminate sample variance.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </main>

  <!-- Application Logic -->
  <script>
    const PLAYERS = ${JSON.stringify(playersData, null, 2)};

    let currentTab = 'roster';
    let currentDiscipline = 'all';
    let currentNationality = 'all';
    let searchQuery = '';
    let sortColumn = 'rank';
    let sortDirection = 'asc';
    let selectedPlayerId = 6288; // Default: Shubman Gill

    let ledgerSlots = {
      1: { role: 'Top-Order Anchor', player: null },
      2: { role: 'Anchor-Elevator', player: null },
      3: { role: 'Middle Spin Demolisher', player: null },
      4: { role: 'Death Power Finisher', player: null },
      5: { role: 'Middle Spin Clamp', player: null },
      6: { role: 'Death Yorker Closer', player: null }
    };

    let bivariateChart = null;
    let holdoutChart = null;

    document.addEventListener('DOMContentLoaded', () => {
      renderTable();
      populateComparatorOptions();
      renderComparison();
      renderLedger();
      openDossier(6288);
      setupKeyboardNavigation();
    });

    function switchTab(tabId) {
      currentTab = tabId;
      document.querySelectorAll('.nav-tab').forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      const activeBtn = document.getElementById('tab-' + tabId);
      if (activeBtn) {
        activeBtn.classList.add('active');
        activeBtn.setAttribute('aria-selected', 'true');
      }

      ['roster', 'quadrant', 'comparator', 'ledger', 'proof'].forEach(id => {
        const view = document.getElementById('view-' + id);
        if (view) view.style.display = (id === tabId) ? 'block' : 'none';
      });

      if (tabId === 'quadrant') renderBivariateChart();
      if (tabId === 'proof') renderHoldoutChart();
    }

    function setDiscipline(val) {
      currentDiscipline = val;
      document.querySelectorAll('.segmented-control button[id^="btn-disc-"]').forEach(b => b.classList.remove('active'));
      const btnMap = { 'all': 'btn-disc-all', 'Batter': 'btn-disc-bat', 'Bowler': 'btn-disc-bowl' };
      if (btnMap[val]) document.getElementById(btnMap[val]).classList.add('active');
      renderTable();
    }

    function setNationality(val) {
      currentNationality = val;
      document.querySelectorAll('.segmented-control button[id^="btn-nat-"]').forEach(b => b.classList.remove('active'));
      const btnMap = { 'all': 'btn-nat-all', 'domestic': 'btn-nat-dom', 'overseas': 'btn-nat-ovs' };
      if (btnMap[val]) document.getElementById(btnMap[val]).classList.add('active');
      renderTable();
    }

    function applyFilters() {
      searchQuery = document.getElementById('searchInput').value.toLowerCase().trim();
      renderTable();
    }

    function getFilteredList() {
      return PLAYERS.filter(p => {
        if (currentDiscipline !== 'all' && p.role !== currentDiscipline) return false;
        if (currentNationality === 'domestic' && p.isOverseas) return false;
        if (currentNationality === 'overseas' && !p.isOverseas) return false;
        if (searchQuery) {
          const matchName = p.name.toLowerCase().includes(searchQuery);
          const matchTeam = p.team.toLowerCase().includes(searchQuery);
          const matchArch = p.archetype.toLowerCase().includes(searchQuery);
          if (!matchName && !matchTeam && !matchArch) return false;
        }
        return true;
      });
    }

    function sortTable(column) {
      if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        sortColumn = column;
        sortDirection = ['score', 'pressureAbility', 'normalAbility', 'uplift', 'certainty', 'balls'].includes(column) ? 'desc' : 'asc';
      }
      renderTable();
    }

    function renderTable() {
      let list = getFilteredList();

      list.sort((a, b) => {
        let vA = a[sortColumn];
        let vB = b[sortColumn];
        if (typeof vA === 'string') {
          return sortDirection === 'asc' ? vA.localeCompare(vB) : vB.localeCompare(vA);
        }
        return sortDirection === 'asc' ? vA - vB : vB - vA;
      });

      document.getElementById('recordCount').textContent = list.length;
      const tbody = document.getElementById('rosterTableBody');
      tbody.innerHTML = '';

      if (list.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" style="text-align: center; padding: 32px; color: var(--ink-muted);">No records match criteria.</td></tr>';
        return;
      }

      list.forEach(p => {
        const tr = document.createElement('tr');
        if (p.id === selectedPlayerId) tr.classList.add('active-row');
        tr.style.cursor = 'pointer';
        tr.onclick = () => openDossier(p.id);

        const scoreFormatted = (p.score >= 0 ? '+' : '') + p.score.toFixed(3);
        const pressFormatted = (p.pressureAbility >= 0 ? '+' : '') + p.pressureAbility.toFixed(3);
        const normFormatted = (p.normalAbility >= 0 ? '+' : '') + p.normalAbility.toFixed(3);
        const upliftFormatted = (p.uplift >= 0 ? '+' : '') + p.uplift.toFixed(3);

        tr.innerHTML = \`
          <td class="rank-number \${p.rank === 1 ? 'top-rank' : ''}">#\${p.rank}</td>
          <td>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="country-pill">\${p.countryCode}</span>
              <div>
                <div class="player-name">\${p.name}</div>
                <div style="font-size: 11px; color: var(--ink-muted);">\${p.archetype}</div>
              </div>
            </div>
          </td>
          <td>\${p.role}</td>
          <td>\${p.team}</td>
          <td style="text-align: right; font-weight: 600; color: \${p.score >= 0.1 ? 'var(--rr-pink)' : 'var(--ink-primary)'};">\${scoreFormatted}</td>
          <td style="text-align: right;">\${pressFormatted}</td>
          <td style="text-align: right; color: var(--ink-muted);">\${normFormatted}</td>
          <td style="text-align: right;" class="\${p.uplift >= 0 ? 'stat-positive' : 'stat-negative'}">\${upliftFormatted}</td>
          <td style="text-align: right;">\${p.certainty.toFixed(1)}%</td>
          <td style="text-align: right;">\${p.balls}</td>
          <td style="text-align: right; color: var(--ink-muted);">\${p.matches}</td>
        \`;
        tbody.appendChild(tr);
      });
    }

    function openDossier(playerId) {
      selectedPlayerId = playerId;
      const p = PLAYERS.find(x => x.id === playerId);
      if (!p) return;

      document.getElementById('workbenchContainer').classList.remove('detail-hidden');
      document.getElementById('dossierPanel').style.display = 'block';

      document.getElementById('dossierRole').textContent = \`#\${p.rank} \${p.role} &bull; \${p.archetype}\`;
      document.getElementById('dossierName').textContent = p.name;
      document.getElementById('dossierTeam').textContent = \`\${p.team} (\${p.countryCode}) &bull; ID: \${p.id} &bull; Valuation: &pound; \${p.auctionPrice} Cr\`;

      document.getElementById('dossierScore').textContent = (p.score >= 0 ? '+' : '') + p.score.toFixed(3);
      document.getElementById('dossierUplift').textContent = (p.uplift >= 0 ? '+' : '') + p.uplift.toFixed(3);
      document.getElementById('dossierPress').textContent = '+' + p.pressureAbility.toFixed(3);
      document.getElementById('dossierCertainty').textContent = p.certainty.toFixed(1) + '%';
      document.getElementById('dossierScouting').textContent = p.scouting;

      const inSquad = Object.values(ledgerSlots).some(s => s.player && s.player.id === p.id);
      const draftBtn = document.getElementById('dossierDraftBtn');
      draftBtn.textContent = inSquad ? 'Remove from Auction Allocation Ledger' : 'Add to Auction Allocation Ledger';

      renderPosteriorCurve(p);
      renderTable();
    }

    function closeDossier() {
      document.getElementById('workbenchContainer').classList.add('detail-hidden');
      document.getElementById('dossierPanel').style.display = 'none';
      selectedPlayerId = null;
      renderTable();
    }

    function togglePlayerFromDossier() {
      if (!selectedPlayerId) return;
      const p = PLAYERS.find(x => x.id === selectedPlayerId);
      if (!p) return;

      const existingSlotKey = Object.keys(ledgerSlots).find(k => ledgerSlots[k].player && ledgerSlots[k].player.id === p.id);
      if (existingSlotKey) {
        ledgerSlots[existingSlotKey].player = null;
        showToast(\`Removed \${p.name} from ledger.\`);
      } else {
        const emptyKey = Object.keys(ledgerSlots).find(k => !ledgerSlots[k].player);
        if (emptyKey) {
          ledgerSlots[emptyKey].player = p;
          showToast(\`Allocated \${p.name} to Slot \${emptyKey} (\${ledgerSlots[emptyKey].role})\`);
        } else {
          showToast('Allocation ledger full. Remove a slot first.');
        }
      }

      openDossier(p.id);
      renderLedger();
    }

    // Mathematical Gaussian Bell Curve Renderer
    function renderPosteriorCurve(p) {
      const canvas = document.getElementById('posteriorCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.width;
      const h = canvas.height;

      ctx.clearRect(0, 0, w, h);

      const mu = p.pressureAbility;
      const q10 = p.score;
      const sigma = (mu - q10) / 1.282;

      const xMin = mu - 3.2 * sigma;
      const xMax = mu + 3.2 * sigma;

      function toX(xVal) { return ((xVal - xMin) / (xMax - xMin)) * (w - 30) + 15; }
      function normalPdf(x) { return (1 / (sigma * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - mu) / sigma, 2)); }
      const maxPdf = normalPdf(mu);
      function toY(pdfVal) { return h - 20 - (pdfVal / maxPdf) * (h - 40); }

      // Shaded credible region
      ctx.beginPath();
      ctx.moveTo(toX(q10), toY(0));
      for (let x = q10; x <= xMax; x += (xMax - q10) / 40) {
        ctx.lineTo(toX(x), toY(normalPdf(x)));
      }
      ctx.lineTo(toX(xMax), toY(0));
      ctx.closePath();
      ctx.fillStyle = 'rgba(194, 0, 91, 0.08)';
      ctx.fill();

      // Normal curve stroke
      ctx.beginPath();
      for (let x = xMin; x <= xMax; x += (xMax - xMin) / 60) {
        const px = toX(x);
        const py = toY(normalPdf(x));
        if (x === xMin) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.strokeStyle = '#001D48';
      ctx.lineWidth = 1.75;
      ctx.stroke();

      // Q0.10 vertical line
      const qX = toX(q10);
      ctx.beginPath();
      ctx.moveTo(qX, 10);
      ctx.lineTo(qX, h - 20);
      ctx.strokeStyle = '#C2005B';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([3, 3]);
      ctx.stroke();
      ctx.setLineDash([]);

      // Baseline
      ctx.beginPath();
      ctx.moveTo(10, h - 20);
      ctx.lineTo(w - 10, h - 20);
      ctx.strokeStyle = '#D1D5DB';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Text markers
      ctx.fillStyle = '#C2005B';
      ctx.font = '600 10px monospace';
      ctx.fillText(\`Q0.10: \${(q10 >= 0 ? '+' : '')}\${q10.toFixed(3)}\`, Math.max(12, qX - 35), 18);
    }

    // Bivariate Performance Map
    function renderBivariateChart() {
      const ctx = document.getElementById('bivariateChart');
      if (!ctx) return;
      if (bivariateChart) bivariateChart.destroy();

      const batters = PLAYERS.filter(p => p.role === 'Batter').map(p => ({
        x: p.normalAbility,
        y: p.pressureAbility,
        player: p
      }));

      const bowlers = PLAYERS.filter(p => p.role === 'Bowler').map(p => ({
        x: p.normalAbility,
        y: p.pressureAbility,
        player: p
      }));

      bivariateChart = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: 'Batters',
              data: batters,
              backgroundColor: '#C2005B',
              borderColor: '#FFFFFF',
              borderWidth: 1.5,
              pointRadius: (ctx) => Math.max(5, Math.min(12, (ctx.raw?.player?.balls || 300) / 45))
            },
            {
              label: 'Bowlers',
              data: bowlers,
              backgroundColor: '#001D48',
              borderColor: '#FFFFFF',
              borderWidth: 1.5,
              pointRadius: (ctx) => Math.max(5, Math.min(12, (ctx.raw?.player?.balls || 300) / 45))
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#FFFFFF',
              titleColor: '#111827',
              bodyColor: '#374151',
              borderColor: '#D1D5DB',
              borderWidth: 1,
              padding: 10,
              displayColors: false,
              callbacks: {
                label: (ctx) => {
                  const p = ctx.raw.player;
                  return [
                    \`\${p.name} (\${p.countryCode} &bull; \${p.role} #\${p.rank})\`,
                    \`Conservative Score: \${p.score >= 0 ? '+' : ''}\${p.score.toFixed(3)} Q0.10\`,
                    \`Pressure Ability: +\${p.pressureAbility.toFixed(3)}\`,
                    \`Normal Baseline: \${p.normalAbility >= 0 ? '+' : ''}\${p.normalAbility.toFixed(3)}\`,
                    \`Empirical Bayes Uplift: +\${p.uplift.toFixed(3)} (Cert: \${p.certainty}%)\`,
                    \`Volume: \${p.balls} legal deliveries across \${p.matches} matches\`
                  ];
                }
              }
            }
          },
          scales: {
            x: {
              title: { display: true, text: 'Normal Game Baseline (\u03BC_norm)', color: '#4B5563', font: { weight: '600' } },
              grid: { color: '#E5E7EB' },
              ticks: { color: '#6B7280' }
            },
            y: {
              title: { display: true, text: 'Pressure Ability (\u03BC_press)', color: '#4B5563', font: { weight: '600' } },
              grid: { color: '#E5E7EB' },
              ticks: { color: '#6B7280' }
            }
          },
          onClick: (evt, elements) => {
            if (elements && elements.length > 0) {
              const datasetIdx = elements[0].datasetIndex;
              const dataIdx = elements[0].index;
              const player = bivariateChart.data.datasets[datasetIdx].data[dataIdx].player;
              switchTab('roster');
              openDossier(player.id);
            }
          }
        }
      });
    }

    // Pairwise Comparator Logic
    function populateComparatorOptions() {
      const selectA = document.getElementById('compareSelectA');
      const selectB = document.getElementById('compareSelectB');
      if (!selectA || !selectB) return;

      selectA.innerHTML = '';
      selectB.innerHTML = '';

      PLAYERS.forEach(p => {
        const optA = document.createElement('option');
        optA.value = p.id;
        optA.textContent = \`\${p.name} (\${p.countryCode} &bull; \${p.role})\`;
        selectA.appendChild(optA);

        const optB = document.createElement('option');
        optB.value = p.id;
        optB.textContent = \`\${p.name} (\${p.countryCode} &bull; \${p.role})\`;
        selectB.appendChild(optB);
      });

      selectA.value = 6288; // Gill
      selectB.value = 6059; // Gaikwad
    }

    function loadComparisonPreset(idA, idB) {
      document.getElementById('compareSelectA').value = idA;
      document.getElementById('compareSelectB').value = idB;
      renderComparison();
    }

    function renderComparison() {
      const idA = parseInt(document.getElementById('compareSelectA').value);
      const idB = parseInt(document.getElementById('compareSelectB').value);
      const pA = PLAYERS.find(x => x.id === idA) || PLAYERS[0];
      const pB = PLAYERS.find(x => x.id === idB) || PLAYERS[1];

      renderCompareColumn('compareCardA', pA, pB);
      renderCompareColumn('compareCardB', pB, pA);
    }

    function renderCompareColumn(containerId, player, opponent) {
      const container = document.getElementById(containerId);
      if (!container) return;

      const diffScore = (player.score - opponent.score).toFixed(3);
      const diffUplift = (player.uplift - opponent.uplift).toFixed(3);

      container.innerHTML = \`
        <div style="border-bottom: 1px solid var(--border-light); padding-bottom: 12px; margin-bottom: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <h3 style="font-size: 18px;">\${player.name}</h3>
            <span class="country-pill">\${player.countryCode}</span>
          </div>
          <div style="font-size: 12px; color: var(--ink-muted); margin-top: 2px;">
            #\${player.rank} \${player.role} &bull; \${player.team} &bull; Est. Cap: &pound; \${player.auctionPrice} Cr
          </div>
        </div>

        <div style="display: flex; flex-direction: column; gap: 8px;">
          <div class="sheet-row">
            <span>Conservative Reliability (Q0.10)</span>
            <span style="font-weight: 700; color: \${player.score >= opponent.score ? 'var(--signal-green)' : 'var(--ink-secondary)'};">
              \${player.score >= 0 ? '+' : ''}\${player.score.toFixed(3)}
              <small style="color: var(--ink-muted); font-weight: normal;">(\${diffScore >= 0 ? '+' : ''}\${diffScore})</small>
            </span>
          </div>

          <div class="sheet-row">
            <span>Clutch Uplift Delta (&Delta;)</span>
            <span style="font-weight: 700; color: \${player.uplift >= opponent.uplift ? 'var(--signal-green)' : 'var(--ink-secondary)'};">
              +\${player.uplift.toFixed(3)}
              <small style="color: var(--ink-muted); font-weight: normal;">(\${diffUplift >= 0 ? '+' : ''}\${diffUplift})</small>
            </span>
          </div>

          <div class="sheet-row">
            <span>Pressure Ability Mean</span>
            <span style="font-weight: 600;">+\${player.pressureAbility.toFixed(3)}</span>
          </div>

          <div class="sheet-row">
            <span>Game Normal Par Baseline</span>
            <span style="font-weight: 600; color: var(--ink-muted);">\${player.normalAbility >= 0 ? '+' : ''}\${player.normalAbility.toFixed(3)}</span>
          </div>

          <div class="sheet-row">
            <span>Posterior Probability P(&Delta; &gt; 0)</span>
            <span style="font-weight: 600;">\${player.certainty.toFixed(1)}%</span>
          </div>

          <div class="sheet-row">
            <span>Sample Volume</span>
            <span>\${player.balls} deliveries (\${player.matches} matches)</span>
          </div>
        </div>

        <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--border-light); font-size: 12px; line-height: 1.5; color: var(--ink-secondary);">
          <strong>Tactical Assessment:</strong> \${player.scouting}
        </div>
      \`;
    }

    // Ledger Logic
    function renderLedger() {
      const tbody = document.getElementById('ledgerTableBody');
      if (!tbody) return;
      tbody.innerHTML = '';

      let filledCount = 0;
      let overseasCount = 0;
      let budgetSum = 0;
      let scoreSum = 0;

      Object.entries(ledgerSlots).forEach(([slotId, slot]) => {
        const p = slot.player;
        if (p) {
          filledCount++;
          if (p.isOverseas) overseasCount++;
          budgetSum += p.auctionPrice;
          scoreSum += p.score;
        }

        const tr = document.createElement('tr');
        if (p) {
          tr.innerHTML = \`
            <td style="font-weight: 600; color: var(--rr-navy);">Slot \${slotId}: \${slot.role}</td>
            <td style="font-weight: 600;">\${p.name}</td>
            <td><span class="country-pill">\${p.countryCode}</span></td>
            <td>\${p.role}</td>
            <td style="text-align: right; font-weight: 600; color: var(--rr-pink);">\${p.score >= 0 ? '+' : ''}\${p.score.toFixed(3)}</td>
            <td style="text-align: right;" class="stat-positive">+\${p.uplift.toFixed(3)}</td>
            <td style="text-align: right; font-weight: 600;">&pound; \${p.auctionPrice.toFixed(1)} Cr</td>
            <td style="text-align: center;">
              <button onclick="removeLedgerSlot(\${slotId})" class="btn" style="padding: 2px 8px; font-size: 11px;">Remove</button>
            </td>
          \`;
        } else {
          tr.innerHTML = \`
            <td style="color: var(--ink-muted); font-weight: 500;">Slot \${slotId}: \${slot.role}</td>
            <td style="color: var(--ink-muted); font-style: italic;">Unallocated</td>
            <td>-</td>
            <td>-</td>
            <td style="text-align: right; color: var(--ink-muted);">-</td>
            <td style="text-align: right; color: var(--ink-muted);">-</td>
            <td style="text-align: right; color: var(--ink-muted);">-</td>
            <td style="text-align: center;">
              <button onclick="quickAssignLedgerSlot(\${slotId})" class="btn" style="padding: 2px 8px; font-size: 11px;">+ Allocate</button>
            </td>
          \`;
        }
        tbody.appendChild(tr);
      });

      document.getElementById('ledgerFilledCount').textContent = \`\${filledCount} / 6\`;
      const ovEl = document.getElementById('ledgerOverseasCount');
      ovEl.textContent = \`\${overseasCount} / 4 Overseas\`;
      ovEl.style.color = (overseasCount > 4) ? 'var(--signal-red)' : 'var(--ink-primary)';

      document.getElementById('ledgerBudgetSum').textContent = \`&pound; \${budgetSum.toFixed(1)} Cr\`;
      document.getElementById('ledgerScoreSum').textContent = (scoreSum >= 0 ? '+' : '') + scoreSum.toFixed(3);
    }

    function removeLedgerSlot(slotId) {
      if (ledgerSlots[slotId]) {
        ledgerSlots[slotId].player = null;
        renderLedger();
        if (selectedPlayerId) openDossier(selectedPlayerId);
      }
    }

    function quickAssignLedgerSlot(slotId) {
      const assignedIds = Object.values(ledgerSlots).filter(s => s.player).map(s => s.player.id);
      const candidate = PLAYERS.find(p => !assignedIds.includes(p.id));
      if (candidate) {
        ledgerSlots[slotId].player = candidate;
        renderLedger();
        if (selectedPlayerId) openDossier(selectedPlayerId);
      }
    }

    function loadLedgerPreset(type) {
      clearLedger();
      if (type === 'fortress') {
        ledgerSlots[1].player = PLAYERS.find(p => p.id === 6288); // Gill
        ledgerSlots[2].player = PLAYERS.find(p => p.id === 5039); // Patidar
        ledgerSlots[3].player = PLAYERS.find(p => p.id === 1318); // Russell
        ledgerSlots[4].player = PLAYERS.find(p => p.id === 781);  // Narine
        ledgerSlots[5].player = PLAYERS.find(p => p.id === 7920); // Ellis
        ledgerSlots[6].player = PLAYERS.find(p => p.id === 2933); // Bumrah
      } else if (type === 'power') {
        ledgerSlots[1].player = PLAYERS.find(p => p.id === 6059); // Gaikwad
        ledgerSlots[2].player = PLAYERS.find(p => p.id === 1699); // Surya
        ledgerSlots[3].player = PLAYERS.find(p => p.id === 6396); // David
        ledgerSlots[4].player = PLAYERS.find(p => p.id === 7364); // Rauf
        ledgerSlots[5].player = PLAYERS.find(p => p.id === 4900); // Hasaranga
        ledgerSlots[6].player = PLAYERS.find(p => p.id === 8661); // Pathirana
      } else if (type === 'domestic') {
        ledgerSlots[1].player = PLAYERS.find(p => p.id === 6288); // Gill
        ledgerSlots[2].player = PLAYERS.find(p => p.id === 6059); // Gaikwad
        ledgerSlots[3].player = PLAYERS.find(p => p.id === 5039); // Patidar
        ledgerSlots[4].player = PLAYERS.find(p => p.id === 7897); // Tilak
        ledgerSlots[5].player = PLAYERS.find(p => p.id === 2261); // Harshal
        ledgerSlots[6].player = PLAYERS.find(p => p.id === 2933); // Bumrah
      }
      renderLedger();
      if (selectedPlayerId) openDossier(selectedPlayerId);
      showToast(\`Loaded preset: \${type}\`);
    }

    function clearLedger() {
      Object.keys(ledgerSlots).forEach(k => ledgerSlots[k].player = null);
      renderLedger();
      if (selectedPlayerId) openDossier(selectedPlayerId);
    }

    // Holdout Validation Chart
    function renderHoldoutChart() {
      const ctx = document.getElementById('holdoutChart');
      if (!ctx) return;
      if (holdoutChart) holdoutChart.destroy();

      holdoutChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Batters Holdout RMSE', 'Bowlers Holdout RMSE'],
          datasets: [
            {
              label: 'Standard Baselines',
              data: [1.6965, 1.0757],
              backgroundColor: '#9CA3AF'
            },
            {
              label: 'RR Model A+ (GBDT + Bayes)',
              data: [1.3688, 0.9131],
              backgroundColor: '#001D48'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top', labels: { font: { size: 11, weight: '600' } } }
          },
          scales: {
            y: {
              title: { display: true, text: 'Prediction Error (Lower is Better)', color: '#4B5563' },
              grid: { color: '#E5E7EB' }
            },
            x: { grid: { display: false } }
          }
        }
      });
    }

    // Keyboard Navigation
    function setupKeyboardNavigation() {
      document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') {
          if (e.key === 'Escape') e.target.blur();
          return;
        }

        if (e.key === '/') {
          e.preventDefault();
          document.getElementById('searchInput').focus();
        } else if (e.key >= '1' && e.key <= '5') {
          const map = { '1': 'roster', '2': 'quadrant', '3': 'comparator', '4': 'ledger', '5': 'proof' };
          switchTab(map[e.key]);
        }
      });
    }

    function showToast(msg) {
      const existing = document.querySelector('.toast');
      if (existing) existing.remove();

      const toast = document.createElement('div');
      toast.className = 'toast';
      toast.textContent = msg;
      document.body.appendChild(toast);

      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(8px)';
        setTimeout(() => toast.remove(), 250);
      }, 2500);
    }

    function exportCSV() {
      let csv = 'rank,role,player_name,country,conservative_score,pressure_ability,normal_ability,uplift,prob_positive_uplift,pressure_balls,pressure_matches\\n';
      PLAYERS.forEach(p => {
        csv += \`\${p.rank},\${p.role},"\${p.name}",\${p.countryCode},\${p.score},\${p.pressureAbility},\${p.normalAbility},\${p.uplift},\${p.certainty}%,\${p.balls},\${p.matches}\\n\`;
      });

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'rajasthan_royals_superr_selector_rankings.csv';
      a.click();
      URL.revokeObjectURL(url);
      showToast('Exported verified rankings to CSV');
    }

    function exportJSON() {
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(PLAYERS, null, 2));
      const a = document.createElement('a');
      a.href = dataStr;
      a.download = 'rajasthan_royals_superr_selector_rankings.json';
      a.click();
      showToast('Exported verified rankings to JSON');
    }
  </script>
</body>
</html>
`;

// Write to reports/dashboard.html
const reportsDashboardPath = path.resolve('/mnt/data/Projects/RR Hackathon/reports/dashboard.html');
fs.writeFileSync(reportsDashboardPath, dashboardHtml, 'utf8');
console.log('Successfully wrote:', reportsDashboardPath);

// Write to dashboard/index.html
const dashboardIndexPath = path.resolve('/mnt/data/Projects/RR Hackathon/dashboard/index.html');
fs.writeFileSync(dashboardIndexPath, dashboardHtml, 'utf8');
console.log('Successfully wrote:', dashboardIndexPath);
