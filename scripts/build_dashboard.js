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
    nationality: 'India',
    flag: '🇮🇳',
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
    radar: [88, 92, 85, 93, 76, 82], // Floor, Peak, Uplift, Certainty, Sample, Baseline
    scouting: 'Masterful anchor who elevates precisely when required rate spikes. Exceptionally low dismissal hazard in high-leverage chases, controlling tempo through field placements.',
    phaseSplit: { powerplay: '+0.12', middle: '+0.18', death: '+0.27' },
    status: 'Retained Franchise Core'
  },
  {
    rank: 2,
    role: 'Batter',
    id: 6059,
    name: 'Ruturaj Gaikwad',
    team: 'India',
    nationality: 'India',
    flag: '🇮🇳',
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
    nationality: 'India',
    flag: '🇮🇳',
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
    nationality: 'Australia',
    flag: '🇦🇺',
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
    scouting: 'Elite normal baseline (+0.280) allows him to clear boundaries against frontline pacers at death without sight balls. Pure terminal power weapon for overs 17–20.',
    phaseSplit: { powerplay: '+0.00', middle: '+0.12', death: '+0.32' },
    status: 'Overseas Power Weapon'
  },
  {
    rank: 5,
    role: 'Batter',
    id: 5039,
    name: 'Rajat Patidar',
    team: 'India',
    nationality: 'India',
    flag: '🇮🇳',
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
    nationality: 'West Indies',
    flag: '🌴',
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
    nationality: 'India',
    flag: '🇮🇳',
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
    nationality: 'India',
    flag: '🇮🇳',
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
    nationality: 'Australia',
    flag: '🇦🇺',
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
    nationality: 'South Africa',
    flag: '🇿🇦',
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
    nationality: 'India',
    flag: '🇮🇳',
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
    nationality: 'Australia',
    flag: '🇦🇺',
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
    nationality: 'Pakistan',
    flag: '🇵🇰',
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
    nationality: 'West Indies',
    flag: '🌴',
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
    nationality: 'India',
    flag: '🇮🇳',
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
    nationality: 'Sri Lanka',
    flag: '🇱🇰',
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
    nationality: 'Sri Lanka',
    flag: '🇱🇰',
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
    nationality: 'India',
    flag: '🇮🇳',
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
    nationality: 'India',
    flag: '🇮🇳',
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
    nationality: 'Bangladesh',
    flag: '🇧🇩',
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
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rajasthan Royals Analytics | SupeRR Selector Executive Command Console</title>
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
  <!-- Lucide Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>
  
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            rr: {
              pink: '#E00070',
              'pink-light': '#FDF2F8',
              'pink-dark': '#BE005F',
              navy: '#001D48',
              'navy-light': '#0B172B',
              'navy-dark': '#060D1A',
              royal: '#004B8C',
              gold: '#FFC72C',
              border: '#1E3A5F',
              card: '#0B172B'
            }
          },
          fontFamily: {
            sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
            mono: ['Consolas', 'Monaco', 'Courier New', 'monospace']
          }
        }
      }
    }
  </script>

  <style>
    /* Custom scrollbars */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.25); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(224, 0, 112, 0.4); }

    /* Print Styles */
    @media print {
      body { background: white !important; color: black !important; }
      .no-print { display: none !important; }
      .print-break { page-break-after: always; }
      .dark { background: white !important; color: black !important; }
    }

    /* Table sticky headers */
    .table-container { max-height: calc(100vh - 360px); }
  </style>
</head>
<body class="bg-[#060D1A] text-slate-100 min-h-screen flex flex-col font-sans transition-colors duration-200 antialiased selection:bg-rr-pink selection:text-white">

  <!-- TOP EXECUTIVE BANNER & GLOBAL HEADER -->
  <header class="border-b border-rr-border/80 bg-[#0B172B]/95 backdrop-blur-md sticky top-0 z-40 px-4 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
    <!-- Brand & Identity -->
    <div class="flex items-center gap-3.5">
      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-rr-pink to-rr-navy flex items-center justify-center font-black text-white text-xl shadow-lg shadow-rr-pink/20 border border-rr-pink/30 flex-shrink-0">
        RR
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h1 class="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            Rajasthan Royals <span class="text-xs px-2 py-0.5 rounded font-mono font-bold bg-rr-pink/20 text-rr-pink border border-rr-pink/40">SUPERR SELECTOR S2</span>
          </h1>
          <span class="hidden md:inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> 100% UNSTOP VERIFIED
          </span>
        </div>
        <p class="text-xs text-slate-400 hidden sm:block">
          Executive Decision Console & Pressure Intelligence Engine • Prepared for Kumar Sangakkara & Giles Lindsay
        </p>
      </div>
    </div>

    <!-- Quick Metric Ticker -->
    <div class="hidden xl:flex items-center gap-6 text-xs bg-[#060D1A]/70 px-4 py-2 rounded-lg border border-rr-border/50">
      <div>
        <div class="text-slate-400 uppercase text-[10px] tracking-wider font-semibold">Deliveries Ingested</div>
        <div class="font-mono font-bold text-white text-sm">200,999 <span class="text-slate-400 font-normal text-xs">(867 Matches)</span></div>
      </div>
      <div class="h-6 w-px bg-slate-800"></div>
      <div>
        <div class="text-slate-400 uppercase text-[10px] tracking-wider font-semibold">High-Pressure Balls</div>
        <div class="font-mono font-bold text-rr-pink text-sm">39,747 <span class="text-slate-400 font-normal text-xs">(19.8%)</span></div>
      </div>
      <div class="h-6 w-px bg-slate-800"></div>
      <div>
        <div class="text-slate-400 uppercase text-[10px] tracking-wider font-semibold">Holdout RMSE Drop</div>
        <div class="font-mono font-bold text-emerald-400 text-sm">-19.3% <span class="text-slate-400 font-normal text-xs">Bat</span> / -15.1% <span class="text-slate-400 font-normal text-xs">Bowl</span></div>
      </div>
    </div>

    <!-- Actions & Global Controls -->
    <div class="flex items-center gap-2.5">
      <!-- Theme Switcher -->
      <button id="themeToggleBtn" aria-label="Toggle Color Theme" class="p-2 rounded-lg bg-slate-800/60 hover:bg-slate-700/60 border border-slate-700/60 text-slate-300 transition-all">
        <i data-lucide="sun" class="w-4 h-4 hidden dark:block text-amber-400"></i>
        <i data-lucide="moon" class="w-4 h-4 block dark:hidden text-rr-navy"></i>
      </button>

      <!-- Keyboard Shortcuts -->
      <button id="shortcutsBtn" aria-label="Keyboard Shortcuts" class="hidden sm:flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-700/60 border border-slate-700/60 text-slate-300 text-xs font-mono transition-all">
        <i data-lucide="keyboard" class="w-3.5 h-3.5"></i>
        <span>?</span>
      </button>

      <!-- Export Menu Dropdown -->
      <div class="relative">
        <button id="exportDropdownBtn" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-rr-pink to-rr-pink-dark text-white text-xs font-semibold shadow-md shadow-rr-pink/20 hover:brightness-110 transition-all">
          <i data-lucide="download" class="w-3.5 h-3.5"></i>
          <span>Export</span>
          <i data-lucide="chevron-down" class="w-3.5 h-3.5 ml-0.5"></i>
        </button>
        <div id="exportMenu" class="hidden absolute right-0 mt-2 w-48 rounded-lg bg-[#0B172B] border border-rr-border shadow-2xl py-1 z-50 text-xs">
          <button onclick="exportCSV()" class="w-full text-left px-3.5 py-2 hover:bg-slate-800/60 text-slate-200 flex items-center gap-2">
            <i data-lucide="file-spreadsheet" class="w-4 h-4 text-emerald-400"></i> Export Dropdown CSV
          </button>
          <button onclick="exportJSON()" class="w-full text-left px-3.5 py-2 hover:bg-slate-800/60 text-slate-200 flex items-center gap-2">
            <i data-lucide="file-code" class="w-4 h-4 text-amber-400"></i> Export Dropdown JSON
          </button>
          <button onclick="window.print()" class="w-full text-left px-3.5 py-2 hover:bg-slate-800/60 text-slate-200 flex items-center gap-2 border-t border-slate-800">
            <i data-lucide="printer" class="w-4 h-4 text-sky-400"></i> Print Executive Sheet
          </button>
        </div>
      </div>
    </div>
  </header>

  <!-- NAVIGATION TABS -->
  <nav class="bg-[#0B172B]/70 border-b border-rr-border px-4 lg:px-8 flex items-center gap-1 overflow-x-auto no-scrollbar" role="tablist">
    <button onclick="switchTab('leaderboard')" id="tab-leaderboard" role="tab" aria-selected="true" class="tab-btn px-4 py-3 text-xs md:text-sm font-semibold border-b-2 border-rr-pink text-rr-pink flex items-center gap-2 whitespace-nowrap transition-all">
      <i data-lucide="trophy" class="w-4 h-4"></i> Leaderboard & Roster Matrix
    </button>
    <button onclick="switchTab('quadrant')" id="tab-quadrant" role="tab" aria-selected="false" class="tab-btn px-4 py-3 text-xs md:text-sm font-semibold border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 whitespace-nowrap transition-all">
      <i data-lucide="compass" class="w-4 h-4"></i> Tactical Quadrant & Phase Simulator
    </button>
    <button onclick="switchTab('comparator')" id="tab-comparator" role="tab" aria-selected="false" class="tab-btn px-4 py-3 text-xs md:text-sm font-semibold border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 whitespace-nowrap transition-all">
      <i data-lucide="swords" class="w-4 h-4"></i> Head-to-Head Comparator
    </button>
    <button onclick="switchTab('warroom')" id="tab-warroom" role="tab" aria-selected="false" class="tab-btn px-4 py-3 text-xs md:text-sm font-semibold border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 whitespace-nowrap transition-all">
      <i data-lucide="gavel" class="w-4 h-4"></i> Auction War Room & Squad Builder
      <span id="squadCountBadge" class="bg-rr-pink text-white text-[10px] px-1.5 py-0.2 rounded-full font-mono font-bold">0</span>
    </button>
    <button onclick="switchTab('diagnostics')" id="tab-diagnostics" role="tab" aria-selected="false" class="tab-btn px-4 py-3 text-xs md:text-sm font-semibold border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 whitespace-nowrap transition-all">
      <i data-lucide="activity" class="w-4 h-4"></i> Model Proof & Architecture
    </button>
  </nav>

  <!-- MAIN VIEW CONTAINER -->
  <main class="flex-1 p-4 lg:p-8 max-w-[1680px] w-full mx-auto space-y-6">

    <!-- ======================================================== -->
    <!-- TAB 1: LEADERBOARD & ROSTER MATRIX -->
    <!-- ======================================================== -->
    <div id="view-leaderboard" class="space-y-6">
      
      <!-- Filter Bar -->
      <section aria-label="Filter Controls" class="bg-rr-card p-4 rounded-xl border border-rr-border shadow-lg flex flex-wrap items-center justify-between gap-4">
        <div class="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">
          <!-- Search Input -->
          <div class="relative flex-1 min-w-[220px]">
            <i data-lucide="search" class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"></i>
            <input type="text" id="searchInput" placeholder="Search player, nationality, or archetype... (Press '/' to focus)" 
              class="w-full bg-[#060D1A] border border-slate-700/80 rounded-lg pl-9 pr-8 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-rr-pink focus:ring-1 focus:ring-rr-pink transition-all">
            <button id="clearSearchBtn" onclick="clearSearch()" class="hidden absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white">
              <i data-lucide="x" class="w-3.5 h-3.5"></i>
            </button>
          </div>

          <!-- Discipline Filter -->
          <div class="inline-flex rounded-lg bg-[#060D1A] p-0.5 border border-slate-700/80 text-xs">
            <button onclick="setFilter('discipline', 'all')" id="filter-disc-all" class="filter-disc-btn px-3 py-1.5 rounded-md font-semibold bg-rr-pink text-white shadow-sm transition-all">All (20)</button>
            <button onclick="setFilter('discipline', 'Batter')" id="filter-disc-batter" class="filter-disc-btn px-3 py-1.5 rounded-md font-semibold text-slate-400 hover:text-white transition-all">Batters (10)</button>
            <button onclick="setFilter('discipline', 'Bowler')" id="filter-disc-bowler" class="filter-disc-btn px-3 py-1.5 rounded-md font-semibold text-slate-400 hover:text-white transition-all">Bowlers (10)</button>
          </div>

          <!-- Nationality Filter -->
          <div class="inline-flex rounded-lg bg-[#060D1A] p-0.5 border border-slate-700/80 text-xs">
            <button onclick="setFilter('nationality', 'all')" id="filter-nat-all" class="filter-nat-btn px-3 py-1.5 rounded-md font-semibold bg-slate-800 text-white transition-all">Global</button>
            <button onclick="setFilter('nationality', 'india')" id="filter-nat-india" class="filter-nat-btn px-3 py-1.5 rounded-md font-semibold text-slate-400 hover:text-white transition-all">India 🇮🇳</button>
            <button onclick="setFilter('nationality', 'overseas')" id="filter-nat-overseas" class="filter-nat-btn px-3 py-1.5 rounded-md font-semibold text-slate-400 hover:text-white transition-all">Overseas 🌍</button>
          </div>
        </div>

        <!-- View Controls & Quick Metrics -->
        <div class="flex items-center gap-3">
          <span class="text-xs text-slate-400 font-mono">Showing <strong id="playerCount" class="text-white">20</strong> players</span>
          <div class="h-4 w-px bg-slate-800"></div>
          <button onclick="toggleViewMode('table')" id="viewModeTableBtn" class="p-1.5 rounded bg-rr-pink text-white shadow-sm">
            <i data-lucide="table" class="w-4 h-4"></i>
          </button>
          <button onclick="toggleViewMode('grid')" id="viewModeGridBtn" class="p-1.5 rounded bg-[#060D1A] text-slate-400 hover:text-white">
            <i data-lucide="layout-grid" class="w-4 h-4"></i>
          </button>
        </div>
      </section>

      <!-- Executive Highlight Cards -->
      <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-rr-card p-4 rounded-xl border border-rr-border hover:border-rr-pink/60 transition-all group">
          <div class="flex items-center justify-between">
            <span class="text-xs uppercase tracking-wider font-semibold text-slate-400">#1 Pressure Batter</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rr-pink/20 text-rr-pink border border-rr-pink/30">TOP ORDER</span>
          </div>
          <div class="mt-2 flex items-baseline justify-between">
            <div class="text-xl font-bold text-white group-hover:text-rr-pink transition-colors">Shubman Gill</div>
            <div class="font-mono text-base font-bold text-rr-pink">+0.140 <span class="text-[10px] font-normal text-slate-400">Q0.10</span></div>
          </div>
          <div class="mt-2 text-xs text-slate-400 flex items-center justify-between pt-2 border-t border-slate-800/80">
            <span>Uplift: <strong class="text-emerald-400">+0.269</strong></span>
            <span>Certainty: <strong class="text-slate-200">92.6%</strong></span>
            <span>204 Balls</span>
          </div>
        </div>

        <div class="bg-rr-card p-4 rounded-xl border border-rr-border hover:border-rr-royal/60 transition-all group">
          <div class="flex items-center justify-between">
            <span class="text-xs uppercase tracking-wider font-semibold text-slate-400">#1 Pressure Bowler</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-sky-950 text-sky-400 border border-sky-800/50">DEATH CLOSER</span>
          </div>
          <div class="mt-2 flex items-baseline justify-between">
            <div class="text-xl font-bold text-white group-hover:text-sky-400 transition-colors">Jasprit Bumrah</div>
            <div class="font-mono text-base font-bold text-sky-400">+0.351 <span class="text-[10px] font-normal text-slate-400">Q0.10</span></div>
          </div>
          <div class="mt-2 text-xs text-slate-400 flex items-center justify-between pt-2 border-t border-slate-800/80">
            <span>Uplift: <strong class="text-emerald-400">+0.423</strong></span>
            <span>Certainty: <strong class="text-emerald-400 font-bold">100.0%</strong></span>
            <span>404 Balls</span>
          </div>
        </div>

        <div class="bg-rr-card p-4 rounded-xl border border-rr-border hover:border-emerald-500/60 transition-all group">
          <div class="flex items-center justify-between">
            <span class="text-xs uppercase tracking-wider font-semibold text-slate-400">Peak Personal Uplift (Δ)</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-950 text-emerald-400 border border-emerald-800/50">CLUTCH SPIKE</span>
          </div>
          <div class="mt-2 flex items-baseline justify-between">
            <div class="text-xl font-bold text-white group-hover:text-emerald-400 transition-colors">Ruturaj Gaikwad</div>
            <div class="font-mono text-base font-bold text-emerald-400">+0.375 <span class="text-[10px] font-normal text-slate-400">runs/ball</span></div>
          </div>
          <div class="mt-2 text-xs text-slate-400 flex items-center justify-between pt-2 border-t border-slate-800/80">
            <span>Base: +0.017</span>
            <span>Pressure: +0.392</span>
            <span>98.6% Cert.</span>
          </div>
        </div>

        <div class="bg-rr-card p-4 rounded-xl border border-rr-border hover:border-amber-500/60 transition-all group">
          <div class="flex items-center justify-between">
            <span class="text-xs uppercase tracking-wider font-semibold text-slate-400">Highest Volume Absorption</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-950 text-amber-400 border border-amber-800/50">RESILIENCE</span>
          </div>
          <div class="mt-2 flex items-baseline justify-between">
            <div class="text-xl font-bold text-white group-hover:text-amber-400 transition-colors">Tilak Varma</div>
            <div class="font-mono text-base font-bold text-amber-400">745 <span class="text-[10px] font-normal text-slate-400">Balls</span></div>
          </div>
          <div class="mt-2 text-xs text-slate-400 flex items-center justify-between pt-2 border-t border-slate-800/80">
            <span>Matches: 54</span>
            <span>Score: -0.004</span>
            <span>81.8% Cert.</span>
          </div>
        </div>
      </section>

      <!-- Table View Container -->
      <section id="tableViewSection" class="bg-rr-card rounded-xl border border-rr-border shadow-xl overflow-hidden">
        <div class="overflow-x-auto table-container">
          <table class="w-full text-left text-xs border-collapse">
            <thead class="bg-[#060D1A]/90 sticky top-0 z-20 text-[11px] uppercase tracking-wider text-slate-400 font-semibold border-b border-rr-border">
              <tr>
                <th scope="col" class="py-3.5 px-4 cursor-pointer hover:text-white" onclick="sortTable('rank')">
                  Rank <span id="sort-rank" class="ml-1 text-[10px]">▼</span>
                </th>
                <th scope="col" class="py-3.5 px-4 cursor-pointer hover:text-white" onclick="sortTable('name')">
                  Player & Role <span id="sort-name" class="ml-1 text-[10px]"></span>
                </th>
                <th scope="col" class="py-3.5 px-4 cursor-pointer hover:text-white" onclick="sortTable('nationality')">
                  Nationality <span id="sort-nationality" class="ml-1 text-[10px]"></span>
                </th>
                <th scope="col" class="py-3.5 px-4 text-right cursor-pointer hover:text-white" onclick="sortTable('score')">
                  Score (Q0.10) <span id="sort-score" class="ml-1 text-[10px]"></span>
                </th>
                <th scope="col" class="py-3.5 px-4 text-right cursor-pointer hover:text-white" onclick="sortTable('pressureAbility')">
                  Pressure Ability <span id="sort-pressureAbility" class="ml-1 text-[10px]"></span>
                </th>
                <th scope="col" class="py-3.5 px-4 text-right cursor-pointer hover:text-white" onclick="sortTable('normalAbility')">
                  Normal Base <span id="sort-normalAbility" class="ml-1 text-[10px]"></span>
                </th>
                <th scope="col" class="py-3.5 px-4 text-right cursor-pointer hover:text-white" onclick="sortTable('uplift')">
                  Uplift (Δ) <span id="sort-uplift" class="ml-1 text-[10px]"></span>
                </th>
                <th scope="col" class="py-3.5 px-4 text-right cursor-pointer hover:text-white" onclick="sortTable('certainty')">
                  P(Δ > 0) <span id="sort-certainty" class="ml-1 text-[10px]"></span>
                </th>
                <th scope="col" class="py-3.5 px-4 text-right cursor-pointer hover:text-white" onclick="sortTable('balls')">
                  Balls <span id="sort-balls" class="ml-1 text-[10px]"></span>
                </th>
                <th scope="col" class="py-3.5 px-4 text-right cursor-pointer hover:text-white" onclick="sortTable('matches')">
                  Matches <span id="sort-matches" class="ml-1 text-[10px]"></span>
                </th>
                <th scope="col" class="py-3.5 px-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody id="playerTableBody" class="divide-y divide-slate-800/60 font-sans">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </section>

      <!-- Card Grid View Container -->
      <section id="gridViewSection" class="hidden grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <!-- Dynamically populated -->
      </section>
    </div>

    <!-- ======================================================== -->
    <!-- TAB 2: TACTICAL QUADRANT & PHASE SIMULATOR -->
    <!-- ======================================================== -->
    <div id="view-quadrant" class="hidden space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Left: Scatter Matrix Plot (2 cols) -->
        <div class="lg:col-span-2 bg-rr-card p-5 rounded-xl border border-rr-border shadow-xl space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div>
              <h2 class="text-base font-bold text-white flex items-center gap-2">
                <i data-lucide="compass" class="w-4 h-4 text-rr-pink"></i> Pressure Ability vs. Normal Baseline Matrix
              </h2>
              <p class="text-xs text-slate-400">
                Quadrants isolate true match-winners from system-dependent volume aggregators.
              </p>
            </div>
            <div class="flex items-center gap-3 text-xs font-semibold">
              <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-rr-pink"></span> Batters</span>
              <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-sky-400"></span> Bowlers</span>
            </div>
          </div>

          <!-- Scatter Chart Container -->
          <div class="relative h-[440px] w-full">
            <canvas id="quadrantScatterChart"></canvas>
          </div>

          <!-- Quadrant Explanatory Grid -->
          <div class="grid grid-cols-2 gap-3 text-xs pt-2">
            <div class="p-2.5 rounded-lg bg-emerald-950/30 border border-emerald-800/40">
              <div class="font-bold text-emerald-400 uppercase text-[10px]">Top-Right: Elite Clutch Superstars</div>
              <p class="text-slate-300 text-[11px] mt-0.5">High baseline skill + positive clutch uplift. (Bumrah, Suryakumar, Gill, Ellis)</p>
            </div>
            <div class="p-2.5 rounded-lg bg-amber-950/30 border border-amber-800/40">
              <div class="font-bold text-amber-400 uppercase text-[10px]">Top-Left: Pure Pressure Elevators</div>
              <p class="text-slate-300 text-[11px] mt-0.5">Moderate regular average, but transforms into lethal executioner under fire. (Harshal, Rauf, Gaikwad)</p>
            </div>
            <div class="p-2.5 rounded-lg bg-sky-950/30 border border-sky-800/40">
              <div class="font-bold text-sky-400 uppercase text-[10px]">Bottom-Right: High Baseline Powerhouses</div>
              <p class="text-slate-300 text-[11px] mt-0.5">Blistering baseline strike rate maintains floor even if clutch delta is muted. (Tim David, Stubbs)</p>
            </div>
            <div class="p-2.5 rounded-lg bg-rose-950/30 border border-rose-800/40">
              <div class="font-bold text-rose-400 uppercase text-[10px]">Bottom-Left: Negative Clutch Distortion</div>
              <p class="text-slate-300 text-[11px] mt-0.5">Performance drops significantly under high leverage. Avoid in death finishes.</p>
            </div>
          </div>
        </div>

        <!-- Right: Real-Time Situational Leverage Simulator (1 col) -->
        <div class="bg-rr-card p-5 rounded-xl border border-rr-border shadow-xl space-y-4 flex flex-col justify-between">
          <div>
            <div class="border-b border-slate-800 pb-3">
              <h2 class="text-base font-bold text-white flex items-center gap-2">
                <i data-lucide="sliders" class="w-4 h-4 text-rr-gold"></i> Live Situation Simulator
              </h2>
              <p class="text-xs text-slate-400">
                Simulate match states to calculate Dynamic Leverage L(s) and Wicket Cost c(s).
              </p>
            </div>

            <!-- Interactive Sliders -->
            <div class="mt-4 space-y-4 text-xs">
              <div>
                <div class="flex justify-between font-semibold mb-1">
                  <span>Balls Remaining:</span>
                  <span id="simBallsVal" class="font-mono text-rr-pink font-bold">24 balls (Overs 16.0)</span>
                </div>
                <input type="range" id="simBalls" min="1" max="120" value="24" class="w-full accent-rr-pink cursor-pointer" oninput="updateSim()">
              </div>

              <div>
                <div class="flex justify-between font-semibold mb-1">
                  <span>Wickets in Hand:</span>
                  <span id="simWktsVal" class="font-mono text-sky-400 font-bold">5 wickets</span>
                </div>
                <input type="range" id="simWkts" min="1" max="10" value="5" class="w-full accent-sky-400 cursor-pointer" oninput="updateSim()">
              </div>

              <div>
                <div class="flex justify-between font-semibold mb-1">
                  <span>Runs Needed:</span>
                  <span id="simRunsVal" class="font-mono text-amber-400 font-bold">48 runs</span>
                </div>
                <input type="range" id="simRuns" min="1" max="150" value="48" class="w-full accent-amber-400 cursor-pointer" oninput="updateSim()">
              </div>
            </div>

            <!-- Dynamic Outputs -->
            <div class="mt-5 p-4 rounded-xl bg-[#060D1A] border border-slate-800 space-y-3">
              <div class="flex justify-between items-center text-xs">
                <span class="text-slate-400">Required Run Rate (RRR):</span>
                <span id="simRRR" class="font-mono font-bold text-white text-sm">12.00 RPO</span>
              </div>
              <div class="flex justify-between items-center text-xs">
                <span class="text-slate-400">Dynamic Leverage L(s):</span>
                <span id="simLeverage" class="font-mono font-bold text-rr-pink text-sm">0.865 (CRITICAL)</span>
              </div>
              <div class="flex justify-between items-center text-xs">
                <span class="text-slate-400">Wicket Value c(s):</span>
                <span id="simWicketVal" class="font-mono font-bold text-emerald-400 text-sm">11.8 runs</span>
              </div>
              <div class="pt-2 border-t border-slate-800">
                <div class="text-[10px] uppercase text-slate-400 font-semibold mb-1">Recommended Deployment</div>
                <div id="simRecommendation" class="text-xs font-semibold text-white">
                  Deploy death yorker specialist (Ellis/Bumrah). Wicket priority: MAXIMUM.
                </div>
              </div>
            </div>
          </div>

          <!-- Phase Par Reference Table -->
          <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800 text-[11px] space-y-1.5">
            <div class="font-bold text-slate-300">Phase Baseline Par Values:</div>
            <div class="flex justify-between text-slate-400"><span>Powerplay (1–6):</span> <strong>7.50 RPO • Dot: 40%</strong></div>
            <div class="flex justify-between text-slate-400"><span>Middle (7–15):</span> <strong>7.80 RPO • Dot: 35%</strong></div>
            <div class="flex justify-between text-slate-400"><span>Death (16–20):</span> <strong>9.90 RPO • Dot: 28%</strong></div>
          </div>
        </div>

      </div>
    </div>

    <!-- ======================================================== -->
    <!-- TAB 3: HEAD-TO-HEAD COMPARATOR -->
    <!-- ======================================================== -->
    <div id="view-comparator" class="hidden space-y-6">
      
      <!-- Selectors Bar -->
      <section class="bg-rr-card p-4 rounded-xl border border-rr-border shadow-lg flex flex-wrap items-center justify-between gap-4">
        <div class="flex flex-wrap items-center gap-4 flex-1">
          <!-- Player A Selector -->
          <div class="flex-1 min-w-[220px]">
            <label for="compPlayerA" class="block text-xs uppercase tracking-wider text-rr-pink font-bold mb-1">Select Player A (Blue / Left)</label>
            <select id="compPlayerA" onchange="renderComparison()" class="w-full bg-[#060D1A] border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-rr-pink font-semibold">
              <!-- populated -->
            </select>
          </div>

          <div class="text-center font-bold text-slate-500 font-mono text-sm pt-4">VS</div>

          <!-- Player B Selector -->
          <div class="flex-1 min-w-[220px]">
            <label for="compPlayerB" class="block text-xs uppercase tracking-wider text-sky-400 font-bold mb-1">Select Player B (Pink / Right)</label>
            <select id="compPlayerB" onchange="renderComparison()" class="w-full bg-[#060D1A] border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-400 font-semibold">
              <!-- populated -->
            </select>
          </div>
        </div>

        <button onclick="loadPresetComparison('gill_gaikwad')" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold transition-all">
          Gill vs. Gaikwad
        </button>
        <button onclick="loadPresetComparison('bumrah_ellis')" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold transition-all">
          Bumrah vs. Ellis
        </button>
      </section>

      <!-- Comparison Battle Display -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Player A Detail Card -->
        <div id="compCardA" class="bg-rr-card p-5 rounded-xl border-t-4 border-rr-pink border-x border-b border-rr-border shadow-xl space-y-4">
          <!-- dynamically rendered -->
        </div>

        <!-- Center Radar Comparison Chart -->
        <div class="bg-rr-card p-5 rounded-xl border border-rr-border shadow-xl flex flex-col justify-between space-y-4">
          <div>
            <h3 class="text-sm font-bold text-white text-center border-b border-slate-800 pb-2">Multi-Axis Trait Polygon</h3>
            <div class="relative h-[280px] w-full mt-2">
              <canvas id="compRadarChart"></canvas>
            </div>
          </div>

          <!-- Tactical Comparison Verdict -->
          <div id="compVerdictBox" class="p-3.5 rounded-xl bg-[#060D1A] border border-slate-800 text-xs space-y-1">
            <!-- dynamic text -->
          </div>
        </div>

        <!-- Player B Detail Card -->
        <div id="compCardB" class="bg-rr-card p-5 rounded-xl border-t-4 border-sky-400 border-x border-b border-rr-border shadow-xl space-y-4">
          <!-- dynamically rendered -->
        </div>
      </div>

    </div>

    <!-- ======================================================== -->
    <!-- TAB 4: AUCTION WAR ROOM & SQUAD BUILDER -->
    <!-- ======================================================== -->
    <div id="view-warroom" class="hidden space-y-6">
      
      <!-- Top Strategy Banner -->
      <section class="bg-gradient-to-r from-[#001D48] via-[#0B172B] to-[#001D48] p-5 rounded-xl border border-rr-border shadow-2xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <span class="text-xs uppercase tracking-wider font-bold text-rr-gold">Rajasthan Royals War Room • IPL 2027 Strategy Console</span>
          <h2 class="text-xl font-bold text-white mt-1">Pressure-Tested Core XI Simulator</h2>
          <p class="text-xs text-slate-300 mt-0.5">
            Assemble the optimal clutch spine while adhering to BCCI / IPL Overseas quota (Max 4 Overseas) and budget allocations.
          </p>
        </div>

        <!-- Quick Presets -->
        <div class="flex flex-wrap items-center gap-2">
          <button onclick="loadSquadPreset('fortress')" class="px-3 py-1.5 rounded-lg bg-sky-950/80 hover:bg-sky-900 text-sky-300 border border-sky-800 text-xs font-semibold transition-all">
            Preset: Fortress Defense
          </button>
          <button onclick="loadSquadPreset('power')" class="px-3 py-1.5 rounded-lg bg-rr-pink/20 hover:bg-rr-pink/30 text-rr-pink border border-rr-pink/50 text-xs font-semibold transition-all">
            Preset: Max Power Chase
          </button>
          <button onclick="loadSquadPreset('domestic')" class="px-3 py-1.5 rounded-lg bg-emerald-950/80 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 text-xs font-semibold transition-all">
            Preset: Indian Spine
          </button>
          <button onclick="clearSquad()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-all">
            Reset
          </button>
        </div>
      </section>

      <!-- Live War Room Telemetry -->
      <section class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="bg-rr-card p-4 rounded-xl border border-rr-border">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">Selected Players</div>
          <div class="text-2xl font-bold font-mono text-white mt-1"><span id="squadCountDisplay">0</span> / 6 <span class="text-xs text-slate-400 font-normal">Core Slots</span></div>
          <div class="text-[10px] text-slate-400 mt-1">Recommended target unit</div>
        </div>

        <div class="bg-rr-card p-4 rounded-xl border border-rr-border">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">Overseas In XI</div>
          <div class="text-2xl font-bold font-mono mt-1" id="squadOverseasDisplay">0 / 4</div>
          <div id="overseasStatusText" class="text-[10px] text-emerald-400 font-semibold mt-1">✓ Within IPL Quota</div>
        </div>

        <div class="bg-rr-card p-4 rounded-xl border border-rr-border">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">Total Estimated Cap</div>
          <div class="text-2xl font-bold font-mono text-rr-gold mt-1">₹<span id="squadBudgetDisplay">0.0</span> Cr</div>
          <div class="text-[10px] text-slate-400 mt-1">Across selected clutch core</div>
        </div>

        <div class="bg-rr-card p-4 rounded-xl border border-rr-border">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">Cumulative Reliability (Σ Q0.10)</div>
          <div class="text-2xl font-bold font-mono text-emerald-400 mt-1" id="squadScoreDisplay">+0.000</div>
          <div class="text-[10px] text-slate-400 mt-1">Combined clutch floor score</div>
        </div>
      </section>

      <!-- War Room Core Slots & Selection Palette -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Left: Drafted Squad Slots (2 cols) -->
        <div class="lg:col-span-2 space-y-4">
          <div class="bg-rr-card p-5 rounded-xl border border-rr-border shadow-xl space-y-3">
            <h3 class="text-sm font-bold text-white flex items-center justify-between border-b border-slate-800 pb-2">
              <span>Rajasthan Royals Pressure Spine (6 Strategic Slots)</span>
              <span class="text-xs font-normal text-slate-400">Click slot or palette below to assign</span>
            </h3>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" id="squadSlotsContainer">
              <!-- Dynamically populated 6 slots -->
            </div>
          </div>
        </div>

        <!-- Right: War Room Strategic Directives & Roster Recommendations (1 col) -->
        <div class="bg-rr-card p-5 rounded-xl border border-rr-border shadow-xl space-y-4">
          <h3 class="text-sm font-bold text-white border-b border-slate-800 pb-2">Giles Lindsay's War Room Directives</h3>
          
          <div class="space-y-3 text-xs">
            <div class="p-3 rounded-lg bg-[#060D1A] border-l-4 border-rr-pink border-y border-r border-slate-800">
              <div class="font-bold text-white">Directive 1: Death Yorker Depth</div>
              <p class="text-slate-300 text-[11px] mt-1">Target Nathan Ellis (#2) or Matheesha Pathirana (#7) to partner with domestic seamers. Both deliver sub-par death ERs under maximum leverage.</p>
            </div>

            <div class="p-3 rounded-lg bg-[#060D1A] border-l-4 border-sky-400 border-y border-r border-slate-800">
              <div class="font-bold text-white">Directive 2: International Strike Spin</div>
              <p class="text-slate-300 text-[11px] mt-1">Acquire Wanindu Hasaranga (+0.254 uplift, 96.8% cert) for middle spin strangulation or Sunil Narine to strangle boundary flow.</p>
            </div>

            <div class="p-3 rounded-lg bg-[#060D1A] border-l-4 border-emerald-400 border-y border-r border-slate-800">
              <div class="font-bold text-white">Directive 3: Domestic Middle Anchor</div>
              <p class="text-slate-300 text-[11px] mt-1">Lock down Tilak Varma (745 balls) or Rajat Patidar (#5) to protect explosive late finishers from early collapses.</p>
            </div>
          </div>

          <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-[11px] text-slate-300">
            <strong class="text-rr-gold">Decision Rule:</strong> Never bid solely on unadjusted T20 strike rates. Demand positive Q0.10 scores to avoid marquee premiums on noise.
          </div>
        </div>

      </div>

    </div>

    <!-- ======================================================== -->
    <!-- TAB 5: MODEL PROOF & DIAGNOSTICS -->
    <!-- ======================================================== -->
    <div id="view-diagnostics" class="hidden space-y-6">
      
      <!-- Holdout Performance Comparison Bar Chart -->
      <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-rr-card p-5 rounded-xl border border-rr-border shadow-xl space-y-4">
          <div class="border-b border-slate-800 pb-3">
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <i data-lucide="bar-chart-3" class="w-4 h-4 text-emerald-400"></i> Out-of-Sample Holdout Verification
            </h2>
            <p class="text-xs text-slate-400">
              Evaluated on 174 held-out subsequent matches across 517 untouched test players.
            </p>
          </div>

          <div class="relative h-[280px] w-full">
            <canvas id="holdoutBarChart"></canvas>
          </div>

          <div class="grid grid-cols-2 gap-3 text-xs">
            <div class="p-3 rounded-lg bg-[#060D1A] border border-slate-800 text-center">
              <div class="text-slate-400 font-semibold uppercase text-[10px]">Batters Holdout RMSE</div>
              <div class="font-mono text-lg font-bold text-emerald-400 mt-1">1.3688 <span class="text-xs text-slate-400 font-normal">vs 1.6965</span></div>
              <div class="text-[10px] text-emerald-400 mt-0.5 font-bold">-19.3% Error Drop (r = 0.640)</div>
            </div>
            <div class="p-3 rounded-lg bg-[#060D1A] border border-slate-800 text-center">
              <div class="text-slate-400 font-semibold uppercase text-[10px]">Bowlers Holdout RMSE</div>
              <div class="font-mono text-lg font-bold text-sky-400 mt-1">0.9131 <span class="text-xs text-slate-400 font-normal">vs 1.0757</span></div>
              <div class="text-[10px] text-sky-400 mt-0.5 font-bold">-15.1% Error Drop (r = 0.643)</div>
            </div>
          </div>
        </div>

        <!-- Jackknife & Bayesian Regularization Proof -->
        <div class="bg-rr-card p-5 rounded-xl border border-rr-border shadow-xl space-y-4">
          <div class="border-b border-slate-800 pb-3">
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <i data-lucide="shield-check" class="w-4 h-4 text-rr-pink"></i> Jackknife & Quantile Sensitivity Proof
            </h2>
            <p class="text-xs text-slate-400">
              Guarantees rankings are resilient against single-match flukes and sample artifacts.
            </p>
          </div>

          <div class="space-y-3 text-xs">
            <div class="p-3.5 rounded-lg bg-[#060D1A] border border-slate-800 space-y-1">
              <div class="font-bold text-white flex items-center justify-between">
                <span>Jackknife Match Exclusion Stability</span>
                <span class="text-emerald-400 font-mono font-bold">≥ 80.0% Preserved</span>
              </div>
              <p class="text-slate-400 text-[11px]">
                Dropping each player's single highest scoring match preserved at least 80% of the Top 10 roster, proving that no player ranks solely due to one heroic 20th-over finish.
              </p>
            </div>

            <div class="p-3.5 rounded-lg bg-[#060D1A] border border-slate-800 space-y-1">
              <div class="font-bold text-white flex items-center justify-between">
                <span>Bayesian Uncertainty Penalty</span>
                <span class="text-rr-pink font-mono font-bold">Score = Q0.10</span>
              </div>
              <p class="text-slate-400 text-[11px]">
                Score = μ - 1.282σ penalizes high posterior standard deviation from limited samples. Ensures only high-volume, reliable executors make the final Rajasthan Royals board.
              </p>
            </div>

            <div class="p-3.5 rounded-lg bg-[#060D1A] border border-slate-800 space-y-1">
              <div class="font-bold text-white flex items-center justify-between">
                <span>Official Unstop Integrity Check</span>
                <span class="text-emerald-400 font-mono font-bold">20 / 20 Verified</span>
              </div>
              <p class="text-slate-400 text-[11px]">
                0 duplicate players in Batters, 0 in Bowlers. Full checksum validation against Unstop platform dropdown roster requirements.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- 4-Stage Mathematical Formulas -->
      <section class="bg-rr-card p-5 rounded-xl border border-rr-border shadow-xl space-y-4">
        <h3 class="text-sm font-bold text-white border-b border-slate-800 pb-2">Mathematical Formulation Hierarchy</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div class="p-3.5 rounded-lg bg-[#060D1A] border-t-2 border-rr-pink border-x border-b border-slate-800 space-y-1.5">
            <span class="text-[10px] font-bold text-rr-pink uppercase">Stage 1</span>
            <div class="font-bold text-white">Context Baseline</div>
            <div class="font-mono text-[11px] text-slate-300 bg-slate-900 p-2 rounded border border-slate-800">
              E[Runs | Balls, Wkts, RRR, Phase]
            </div>
            <p class="text-slate-400 text-[11px]">Conditions par dynamically on continuous state.</p>
          </div>

          <div class="p-3.5 rounded-lg bg-[#060D1A] border-t-2 border-sky-400 border-x border-b border-slate-800 space-y-1.5">
            <span class="text-[10px] font-bold text-sky-400 uppercase">Stage 2</span>
            <div class="font-bold text-white">Leverage Volatility</div>
            <div class="font-mono text-[11px] text-slate-300 bg-slate-900 p-2 rounded border border-slate-800">
              L(s) = sqrt(Σ P(o)[p_o - p_bar]^2)
            </div>
            <p class="text-slate-400 text-[11px]">Top 20% quantile (L ≥ Q0.80) defines pure match pressure.</p>
          </div>

          <div class="p-3.5 rounded-lg bg-[#060D1A] border-t-2 border-emerald-400 border-x border-b border-slate-800 space-y-1.5">
            <span class="text-[10px] font-bold text-emerald-400 uppercase">Stage 3</span>
            <div class="font-bold text-white">Run-Equivalent V</div>
            <div class="font-mono text-[11px] text-slate-300 bg-slate-900 p-2 rounded border border-slate-800">
              V_bat = r_runs + c(s) · r_surv
            </div>
            <p class="text-slate-400 text-[11px]">Dynamic wicket pricing c(s) scales from 6.0 to 12.0 runs.</p>
          </div>

          <div class="p-3.5 rounded-lg bg-[#060D1A] border-t-2 border-amber-400 border-x border-b border-slate-800 space-y-1.5">
            <span class="text-[10px] font-bold text-amber-400 uppercase">Stage 4</span>
            <div class="font-bold text-white">Conservative Q0.10</div>
            <div class="font-mono text-[11px] text-slate-300 bg-slate-900 p-2 rounded border border-slate-800">
              Score = μ_i - 1.282 · σ_i
            </div>
            <p class="text-slate-400 text-[11px]">Guarantees 90% statistical lower bound performance.</p>
          </div>
        </div>
      </section>

    </div>

  </main>

  <!-- ======================================================== -->
  <!-- PLAYER DEEP-DIVE SLIDE-OVER DRAWER -->
  <!-- ======================================================== -->
  <div id="playerDrawerOverlay" onclick="closePlayerDrawer()" class="hidden fixed inset-0 bg-black/70 backdrop-blur-sm z-50 transition-opacity"></div>
  <aside id="playerDrawer" class="fixed top-0 right-0 h-full w-full max-w-lg bg-[#0B172B] border-l border-rr-border shadow-2xl z-50 transform translate-x-full transition-transform duration-300 flex flex-col overflow-hidden" role="dialog" aria-modal="true" aria-labelledby="drawerPlayerName">
    <!-- Drawer Header -->
    <div class="p-5 border-b border-slate-800 flex items-center justify-between bg-[#060D1A]/80">
      <div class="flex items-center gap-3">
        <div id="drawerAvatar" class="w-11 h-11 rounded-lg bg-rr-pink text-white flex items-center justify-center font-bold text-lg shadow-md">
          --
        </div>
        <div>
          <h3 id="drawerPlayerName" class="text-base font-bold text-white flex items-center gap-2">
            Loading...
          </h3>
          <p id="drawerPlayerMeta" class="text-xs text-slate-400 font-mono">
            Role • ID: 0000
          </p>
        </div>
      </div>
      <button onclick="closePlayerDrawer()" aria-label="Close Drawer" class="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white transition-all">
        <i data-lucide="x" class="w-4 h-4"></i>
      </button>
    </div>

    <!-- Drawer Body -->
    <div class="flex-1 p-5 overflow-y-auto space-y-5 text-xs">
      
      <!-- Score Metric Header -->
      <div class="grid grid-cols-3 gap-2 text-center">
        <div class="p-3 bg-[#060D1A] rounded-xl border border-slate-800">
          <div class="text-[10px] text-slate-400 uppercase font-semibold">Conservative Score</div>
          <div id="drawerScore" class="font-mono text-base font-bold text-rr-pink mt-1">+0.000</div>
          <div class="text-[9px] text-slate-500 font-mono">10th percentile</div>
        </div>
        <div class="p-3 bg-[#060D1A] rounded-xl border border-slate-800">
          <div class="text-[10px] text-slate-400 uppercase font-semibold">Clutch Uplift (Δ)</div>
          <div id="drawerUplift" class="font-mono text-base font-bold text-emerald-400 mt-1">+0.000</div>
          <div id="drawerCertainty" class="text-[9px] text-slate-400 font-mono">0.0% Cert.</div>
        </div>
        <div class="p-3 bg-[#060D1A] rounded-xl border border-slate-800">
          <div class="text-[10px] text-slate-400 uppercase font-semibold">Pressure Balls</div>
          <div id="drawerBalls" class="font-mono text-base font-bold text-sky-400 mt-1">0</div>
          <div id="drawerMatches" class="text-[9px] text-slate-400 font-mono">0 matches</div>
        </div>
      </div>

      <!-- Bayesian Gaussian Bell Curve Visualizer -->
      <div class="p-4 bg-[#060D1A] rounded-xl border border-slate-800 space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-white flex items-center gap-1.5">
            <i data-lucide="activity" class="w-3.5 h-3.5 text-rr-pink"></i> Posterior Ability Distribution
          </span>
          <span class="text-[10px] font-mono text-slate-400">Normal Posterior Curve</span>
        </div>
        <div class="relative h-36 w-full">
          <canvas id="bellCurveCanvas" width="440" height="144" class="w-full h-full"></canvas>
        </div>
        <p class="text-[11px] text-slate-400">
          Pink vertical bar marks the <strong>Q0.10 Conservative Score</strong>. The shaded region denotes 90% credible certainty against sample variance.
        </p>
      </div>

      <!-- Phase Breakdown -->
      <div class="p-4 bg-[#060D1A] rounded-xl border border-slate-800 space-y-2.5">
        <h4 class="font-bold text-white">Estimated Phase-by-Phase Impact</h4>
        <div class="grid grid-cols-3 gap-2 text-center text-xs">
          <div class="p-2 rounded bg-slate-900 border border-slate-800">
            <div class="text-[10px] text-slate-400">Powerplay (1–6)</div>
            <div id="drawerPP" class="font-mono font-bold text-white mt-0.5">+0.00</div>
          </div>
          <div class="p-2 rounded bg-slate-900 border border-slate-800">
            <div class="text-[10px] text-slate-400">Middle (7–15)</div>
            <div id="drawerMid" class="font-mono font-bold text-white mt-0.5">+0.00</div>
          </div>
          <div class="p-2 rounded bg-slate-900 border border-slate-800">
            <div class="text-[10px] text-slate-400">Death (16–20)</div>
            <div id="drawerDeath" class="font-mono font-bold text-rr-pink mt-0.5">+0.00</div>
          </div>
        </div>
      </div>

      <!-- Tactical Scouting Notes -->
      <div class="p-4 bg-[#060D1A] rounded-xl border border-slate-800 space-y-2">
        <h4 class="font-bold text-white flex items-center gap-1.5">
          <i data-lucide="file-text" class="w-3.5 h-3.5 text-rr-gold"></i> RR War Room Scouting Note
        </h4>
        <p id="drawerScouting" class="text-slate-300 text-xs leading-relaxed">
          Loading scouting profile...
        </p>
      </div>

      <!-- Action Button -->
      <div class="pt-2">
        <button id="drawerAddSquadBtn" onclick="togglePlayerInSquadFromDrawer()" class="w-full py-2.5 rounded-lg bg-gradient-to-r from-rr-pink to-rr-pink-dark text-white font-semibold flex items-center justify-center gap-2 hover:brightness-110 shadow-lg shadow-rr-pink/20 transition-all">
          <i data-lucide="plus-circle" class="w-4 h-4"></i> Add to Rajasthan Royals Target Core
        </button>
      </div>

    </div>
  </aside>

  <!-- KEYBOARD SHORTCUTS MODAL -->
  <dialog id="shortcutsModal" class="rounded-xl bg-[#0B172B] text-slate-200 border border-rr-border p-6 shadow-2xl max-w-md w-full backdrop:bg-black/70">
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <h3 class="font-bold text-white flex items-center gap-2">
        <i data-lucide="keyboard" class="w-4 h-4 text-rr-pink"></i> Keyboard Shortcuts
      </h3>
      <button onclick="document.getElementById('shortcutsModal').close()" class="p-1 rounded text-slate-400 hover:text-white">
        <i data-lucide="x" class="w-4 h-4"></i>
      </button>
    </div>
    <div class="mt-4 space-y-2.5 text-xs">
      <div class="flex justify-between items-center py-1 border-b border-slate-800/60">
        <span>Focus Search Bar</span> <kbd class="px-2 py-0.5 bg-slate-800 rounded font-mono font-bold text-rr-pink">/</kbd>
      </div>
      <div class="flex justify-between items-center py-1 border-b border-slate-800/60">
        <span>Switch Tabs</span> <kbd class="px-2 py-0.5 bg-slate-800 rounded font-mono font-bold text-white">1 - 5</kbd>
      </div>
      <div class="flex justify-between items-center py-1 border-b border-slate-800/60">
        <span>Toggle Dark / Light Theme</span> <kbd class="px-2 py-0.5 bg-slate-800 rounded font-mono font-bold text-white">T</kbd>
      </div>
      <div class="flex justify-between items-center py-1 border-b border-slate-800/60">
        <span>Close Modal / Drawer</span> <kbd class="px-2 py-0.5 bg-slate-800 rounded font-mono font-bold text-white">Esc</kbd>
      </div>
      <div class="flex justify-between items-center py-1">
        <span>Show This Cheat Sheet</span> <kbd class="px-2 py-0.5 bg-slate-800 rounded font-mono font-bold text-white">?</kbd>
      </div>
    </div>
  </dialog>

  <!-- TOAST NOTIFICATION CONTAINER -->
  <div id="toastContainer" class="fixed bottom-6 right-6 z-50 space-y-2 pointer-events-none"></div>

  <!-- APPLICATION SCRIPT LOGIC -->
  <script>
    // Injected Dataset
    const PLAYERS = ${JSON.stringify(playersData, null, 2)};

    // State Variables
    let currentTab = 'leaderboard';
    let currentFilter = { discipline: 'all', nationality: 'all', search: '' };
    let currentSort = { column: 'rank', direction: 'asc' };
    let activePlayerDrawer = null;
    let viewMode = 'table'; // 'table' or 'grid'

    // Squad State
    let squadSlots = {
      1: { role: 'Top-Order Anchor', player: null },
      2: { role: 'Anchor-Elevator', player: null },
      3: { role: 'Middle Spin Demolisher', player: null },
      4: { role: 'Death Power Finisher', player: null },
      5: { role: 'Middle Spin Clamp', player: null },
      6: { role: 'Death Yorker Closer', player: null }
    };

    // Chart instances
    let scatterChart = null;
    let radarChart = null;
    let holdoutChart = null;

    // Initialize on DOM load
    document.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      initTheme();
      renderTable();
      populateComparatorSelectors();
      renderSquadSlots();
      setupKeyboardShortcuts();
      initHoldoutChart();
    });

    // Theme Switcher
    function initTheme() {
      const savedTheme = localStorage.getItem('rr_theme') || 'dark';
      if (savedTheme === 'light') {
        document.documentElement.classList.remove('dark');
        document.body.classList.add('bg-slate-50', 'text-slate-900');
        document.body.classList.remove('bg-[#060D1A]', 'text-slate-100');
      } else {
        document.documentElement.classList.add('dark');
      }

      document.getElementById('themeToggleBtn').addEventListener('click', toggleTheme);
    }

    function toggleTheme() {
      const isDark = document.documentElement.classList.contains('dark');
      if (isDark) {
        document.documentElement.classList.remove('dark');
        document.body.classList.add('bg-slate-50', 'text-slate-900');
        document.body.classList.remove('bg-[#060D1A]', 'text-slate-100');
        localStorage.setItem('rr_theme', 'light');
        showToast('Switched to Royal Stadium Light Theme');
      } else {
        document.documentElement.classList.add('dark');
        document.body.classList.remove('bg-slate-50', 'text-slate-900');
        document.body.classList.add('bg-[#060D1A]', 'text-slate-100');
        localStorage.setItem('rr_theme', 'dark');
        showToast('Switched to Midnight Navy Theme');
      }
      lucide.createIcons();
      if (scatterChart) scatterChart.update();
      if (radarChart) radarChart.update();
      if (holdoutChart) holdoutChart.update();
    }

    // Tab Switching
    function switchTab(tabId) {
      currentTab = tabId;
      document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.setAttribute('aria-selected', 'false');
        btn.classList.remove('border-rr-pink', 'text-rr-pink');
        btn.classList.add('border-transparent', 'text-slate-400');
      });

      const activeBtn = document.getElementById('tab-' + tabId);
      if (activeBtn) {
        activeBtn.setAttribute('aria-selected', 'true');
        activeBtn.classList.add('border-rr-pink', 'text-rr-pink');
        activeBtn.classList.remove('border-transparent', 'text-slate-400');
      }

      const tabs = ['leaderboard', 'quadrant', 'comparator', 'warroom', 'diagnostics'];
      tabs.forEach(t => {
        const el = document.getElementById('view-' + t);
        if (el) el.classList.toggle('hidden', t !== tabId);
      });

      // Trigger charts resize/render when tabs become visible
      if (tabId === 'quadrant') initScatterChart();
      if (tabId === 'comparator') renderComparison();
      if (tabId === 'diagnostics') initHoldoutChart();

      lucide.createIcons();
    }

    // Filtering
    function setFilter(type, value) {
      currentFilter[type] = value;
      
      // Update UI buttons
      if (type === 'discipline') {
        document.querySelectorAll('.filter-disc-btn').forEach(b => {
          b.classList.remove('bg-rr-pink', 'text-white', 'shadow-sm');
          b.classList.add('text-slate-400');
        });
        const active = document.getElementById('filter-disc-' + value.toLowerCase());
        if (active) {
          active.classList.add('bg-rr-pink', 'text-white', 'shadow-sm');
          active.classList.remove('text-slate-400');
        }
      }

      if (type === 'nationality') {
        document.querySelectorAll('.filter-nat-btn').forEach(b => {
          b.classList.remove('bg-slate-800', 'text-white');
          b.classList.add('text-slate-400');
        });
        const active = document.getElementById('filter-nat-' + value.toLowerCase());
        if (active) {
          active.classList.add('bg-slate-800', 'text-white');
          active.classList.remove('text-slate-400');
        }
      }

      renderTable();
    }

    // Search input handler
    document.getElementById('searchInput').addEventListener('input', (e) => {
      currentFilter.search = e.target.value.toLowerCase().trim();
      document.getElementById('clearSearchBtn').classList.toggle('hidden', currentFilter.search.length === 0);
      renderTable();
    });

    function clearSearch() {
      document.getElementById('searchInput').value = '';
      currentFilter.search = '';
      document.getElementById('clearSearchBtn').classList.add('hidden');
      renderTable();
    }

    // Filter Logic
    function getFilteredPlayers() {
      return PLAYERS.filter(p => {
        if (currentFilter.discipline !== 'all' && p.role !== currentFilter.discipline) return false;
        if (currentFilter.nationality === 'india' && p.isOverseas) return false;
        if (currentFilter.nationality === 'overseas' && !p.isOverseas) return false;
        if (currentFilter.search) {
          const matchName = p.name.toLowerCase().includes(currentFilter.search);
          const matchTeam = p.team.toLowerCase().includes(currentFilter.search);
          const matchArch = p.archetype.toLowerCase().includes(currentFilter.search);
          if (!matchName && !matchTeam && !matchArch) return false;
        }
        return true;
      });
    }

    // Sort Logic
    function sortTable(column) {
      if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
      } else {
        currentSort.column = column;
        currentSort.direction = (column === 'score' || column === 'pressureAbility' || column === 'uplift' || column === 'certainty' || column === 'balls') ? 'desc' : 'asc';
      }

      // Update indicator arrows
      ['rank', 'name', 'nationality', 'score', 'pressureAbility', 'normalAbility', 'uplift', 'certainty', 'balls', 'matches'].forEach(col => {
        const span = document.getElementById('sort-' + col);
        if (span) span.textContent = (col === column) ? (currentSort.direction === 'asc' ? '▲' : '▼') : '';
      });

      renderTable();
    }

    function toggleViewMode(mode) {
      viewMode = mode;
      document.getElementById('tableViewSection').classList.toggle('hidden', mode !== 'table');
      document.getElementById('gridViewSection').classList.toggle('hidden', mode !== 'grid');
      
      const tableBtn = document.getElementById('viewModeTableBtn');
      const gridBtn = document.getElementById('viewModeGridBtn');
      if (mode === 'table') {
        tableBtn.classList.add('bg-rr-pink', 'text-white');
        tableBtn.classList.remove('bg-[#060D1A]', 'text-slate-400');
        gridBtn.classList.remove('bg-rr-pink', 'text-white');
        gridBtn.classList.add('bg-[#060D1A]', 'text-slate-400');
      } else {
        gridBtn.classList.add('bg-rr-pink', 'text-white');
        gridBtn.classList.remove('bg-[#060D1A]', 'text-slate-400');
        tableBtn.classList.remove('bg-rr-pink', 'text-white');
        tableBtn.classList.add('bg-[#060D1A]', 'text-slate-400');
      }
      renderTable();
    }

    // Render Table
    function renderTable() {
      let list = getFilteredPlayers();

      // Sort
      list.sort((a, b) => {
        let valA = a[currentSort.column];
        let valB = b[currentSort.column];
        if (typeof valA === 'string') {
          return currentSort.direction === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
        }
        return currentSort.direction === 'asc' ? valA - valB : valB - valA;
      });

      document.getElementById('playerCount').textContent = list.length;

      // Table body
      const tbody = document.getElementById('playerTableBody');
      tbody.innerHTML = '';

      // Grid container
      const grid = document.getElementById('gridViewSection');
      grid.innerHTML = '';

      if (list.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" class="py-12 text-center text-slate-400">No players match the selected filters.</td></tr>';
        grid.innerHTML = '<div class="col-span-4 py-12 text-center text-slate-400">No players match the selected filters.</div>';
        return;
      }

      list.forEach(p => {
        const isBatter = p.role === 'Batter';
        const scoreColor = p.score >= 0.1 ? 'text-rr-pink font-bold' : (p.score >= 0 ? 'text-white font-semibold' : 'text-slate-400 font-normal');
        const upliftColor = p.uplift > 0.15 ? 'text-emerald-400 font-bold' : (p.uplift > 0 ? 'text-emerald-300' : 'text-rose-400');
        const scoreFormatted = (p.score >= 0 ? '+' : '') + p.score.toFixed(3);
        const upliftFormatted = (p.uplift >= 0 ? '+' : '') + p.uplift.toFixed(3);
        const pressFormatted = (p.pressureAbility >= 0 ? '+' : '') + p.pressureAbility.toFixed(3);
        const normFormatted = (p.normalAbility >= 0 ? '+' : '') + p.normalAbility.toFixed(3);

        const inSquad = Object.values(squadSlots).some(s => s.player && s.player.id === p.id);

        // TABLE ROW
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 transition-colors group cursor-pointer';
        tr.onclick = (e) => {
          if (!e.target.closest('button')) openPlayerDrawer(p.id);
        };

        tr.innerHTML = \`
          <td class="py-3.5 px-4 font-mono font-bold \${p.rank === 1 ? 'text-rr-pink' : (p.rank <= 3 ? 'text-white' : 'text-slate-400')}">
            #\${p.rank}
          </td>
          <td class="py-3.5 px-4">
            <div class="flex items-center gap-2.5">
              <span class="text-base">\${p.flag}</span>
              <div>
                <div class="font-bold text-white group-hover:text-rr-pink transition-colors flex items-center gap-1.5">
                  \${p.name}
                  <span class="text-[9px] px-1.5 py-0.2 rounded font-mono font-semibold \${isBatter ? 'bg-rr-pink/20 text-rr-pink border border-rr-pink/30' : 'bg-sky-950 text-sky-400 border border-sky-800/50'}">
                    \${p.role.toUpperCase()}
                  </span>
                </div>
                <div class="text-[11px] text-slate-400">\${p.archetype}</div>
              </div>
            </div>
          </td>
          <td class="py-3.5 px-4 text-slate-300">
            \${p.nationality}
          </td>
          <td class="py-3.5 px-4 text-right font-mono \${scoreColor}">
            \${scoreFormatted}
          </td>
          <td class="py-3.5 px-4 text-right font-mono text-slate-200">
            \${pressFormatted}
          </td>
          <td class="py-3.5 px-4 text-right font-mono text-slate-400">
            \${normFormatted}
          </td>
          <td class="py-3.5 px-4 text-right font-mono \${upliftColor}">
            \${upliftFormatted}
          </td>
          <td class="py-3.5 px-4 text-right font-mono text-slate-200">
            \${p.certainty.toFixed(1)}%
          </td>
          <td class="py-3.5 px-4 text-right font-mono text-slate-300">
            \${p.balls}
          </td>
          <td class="py-3.5 px-4 text-right font-mono text-slate-400">
            \${p.matches}
          </td>
          <td class="py-3.5 px-4 text-center">
            <div class="inline-flex items-center gap-1">
              <button onclick="openPlayerDrawer(\${p.id})" title="View Deep Dive" class="p-1.5 rounded hover:bg-slate-700/60 text-slate-400 hover:text-white transition-all">
                <i data-lucide="eye" class="w-3.5 h-3.5"></i>
              </button>
              <button onclick="togglePlayerInSquad(\${p.id})" title="\${inSquad ? 'Remove from Squad' : 'Draft into RR Squad'}" class="p-1.5 rounded \${inSquad ? 'bg-rr-pink text-white' : 'hover:bg-slate-700/60 text-slate-400 hover:text-rr-pink'} transition-all">
                <i data-lucide="\${inSquad ? 'check' : 'plus'}" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          </td>
        \`;
        tbody.appendChild(tr);

        // GRID CARD
        const card = document.createElement('div');
        card.className = 'bg-[#060D1A] rounded-xl border border-slate-800/80 p-4 hover:border-rr-pink/60 transition-all flex flex-col justify-between space-y-3 cursor-pointer group shadow-lg';
        card.onclick = (e) => {
          if (!e.target.closest('button')) openPlayerDrawer(p.id);
        };

        card.innerHTML = \`
          <div>
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-2">
                <span class="text-xl">\${p.flag}</span>
                <div>
                  <h4 class="font-bold text-white group-hover:text-rr-pink transition-colors flex items-center gap-1.5">
                    \${p.name}
                  </h4>
                  <span class="text-[10px] text-slate-400">\${p.archetype}</span>
                </div>
              </div>
              <span class="font-mono font-bold text-xs px-2 py-0.5 rounded \${p.rank === 1 ? 'bg-rr-pink text-white' : 'bg-slate-800 text-slate-300'}">
                #\${p.rank}
              </span>
            </div>

            <div class="mt-3 grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/60">
              <div class="p-2 rounded bg-slate-900/60">
                <span class="text-[9px] uppercase tracking-wider text-slate-400">Score (Q0.10)</span>
                <div class="font-mono text-sm font-bold \${scoreColor}">\${scoreFormatted}</div>
              </div>
              <div class="p-2 rounded bg-slate-900/60">
                <span class="text-[9px] uppercase tracking-wider text-slate-400">Clutch Uplift</span>
                <div class="font-mono text-sm font-bold \${upliftColor}">\${upliftFormatted}</div>
              </div>
            </div>

            <div class="mt-2 text-[11px] text-slate-400 flex justify-between">
              <span>Certainty: <strong class="text-slate-200">\${p.certainty.toFixed(1)}%</strong></span>
              <span>Sample: <strong class="text-slate-200">\${p.balls}b</strong> (\${p.matches}m)</span>
            </div>
          </div>

          <div class="pt-2 border-t border-slate-800 flex items-center justify-between">
            <button onclick="openPlayerDrawer(\${p.id})" class="text-xs text-slate-400 hover:text-white font-semibold flex items-center gap-1">
              <i data-lucide="eye" class="w-3.5 h-3.5"></i> Deep Dive
            </button>
            <button onclick="togglePlayerInSquad(\${p.id})" class="px-2.5 py-1 rounded text-xs font-semibold \${inSquad ? 'bg-rr-pink text-white' : 'bg-slate-800 hover:bg-slate-700 text-slate-200'} transition-all flex items-center gap-1">
              <i data-lucide="\${inSquad ? 'check' : 'plus'}" class="w-3.5 h-3.5"></i> \${inSquad ? 'Drafted' : 'Draft'}
            </button>
          </div>
        \`;
        grid.appendChild(card);
      });

      lucide.createIcons();
    }

    // ==========================================
    // TAB 2: SCATTER PLOT & SIMULATOR LOGIC
    // ==========================================
    function initScatterChart() {
      const ctx = document.getElementById('quadrantScatterChart');
      if (!ctx) return;

      if (scatterChart) scatterChart.destroy();

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

      scatterChart = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: 'Batters',
              data: batters,
              backgroundColor: '#E00070',
              borderColor: '#FFFFFF',
              borderWidth: 1.5,
              pointRadius: (ctx) => {
                const b = ctx.raw?.player?.balls || 300;
                return Math.max(6, Math.min(14, b / 45));
              },
              pointHoverRadius: 16
            },
            {
              label: 'Bowlers',
              data: bowlers,
              backgroundColor: '#38BDF8',
              borderColor: '#FFFFFF',
              borderWidth: 1.5,
              pointRadius: (ctx) => {
                const b = ctx.raw?.player?.balls || 300;
                return Math.max(6, Math.min(14, b / 45));
              },
              pointHoverRadius: 16
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#0B172B',
              borderColor: '#1E3A5F',
              borderWidth: 1,
              titleColor: '#FFFFFF',
              bodyColor: '#E2E8F0',
              padding: 10,
              callbacks: {
                label: (ctx) => {
                  const p = ctx.raw.player;
                  return [
                    \`\${p.flag} \${p.name} (#\${p.rank} \${p.role})\`,
                    \`Score: \${p.score >= 0 ? '+' : ''}\${p.score.toFixed(3)} (Q0.10)\`,
                    \`Pressure Ability: +\${p.pressureAbility.toFixed(3)}\`,
                    \`Normal Baseline: \${p.normalAbility >= 0 ? '+' : ''}\${p.normalAbility.toFixed(3)}\`,
                    \`Uplift: +\${p.uplift.toFixed(3)} (Cert: \${p.certainty}%)\`,
                    \`Volume: \${p.balls} balls in \${p.matches} matches\`
                  ];
                }
              }
            }
          },
          scales: {
            x: {
              title: {
                display: true,
                text: 'Normal Baseline Ability μ_norm (Unadjusted Game Par)',
                color: '#94A3B8',
                font: { size: 11, weight: 'bold' }
              },
              grid: { color: 'rgba(148, 163, 184, 0.1)' },
              ticks: { color: '#94A3B8' }
            },
            y: {
              title: {
                display: true,
                text: 'Pressure Ability μ_press (High Leverage L ≥ Q0.80)',
                color: '#94A3B8',
                font: { size: 11, weight: 'bold' }
              },
              grid: { color: 'rgba(148, 163, 184, 0.1)' },
              ticks: { color: '#94A3B8' }
            }
          },
          onClick: (evt, elements) => {
            if (elements && elements.length > 0) {
              const datasetIdx = elements[0].datasetIndex;
              const dataIdx = elements[0].index;
              const dataset = scatterChart.data.datasets[datasetIdx];
              const player = dataset.data[dataIdx].player;
              openPlayerDrawer(player.id);
            }
          }
        }
      });
    }

    // Situation Simulator logic
    function updateSim() {
      const balls = parseInt(document.getElementById('simBalls').value);
      const wkts = parseInt(document.getElementById('simWkts').value);
      const runs = parseInt(document.getElementById('simRuns').value);

      document.getElementById('simBallsVal').textContent = \`\${balls} balls (Over \${(20 - balls/6).toFixed(1)})\`;
      document.getElementById('simWktsVal').textContent = \`\${wkts} wickets\`;
      document.getElementById('simRunsVal').textContent = \`\${runs} runs\`;

      const rrr = ((runs / balls) * 6).toFixed(2);
      document.getElementById('simRRR').textContent = \`\${rrr} RPO\`;

      // Leverage approximation formula
      let leverageScore = 0.5 + (runs / balls) * 0.05 + (10 - wkts) * 0.03;
      if (balls <= 18) leverageScore *= 1.35;
      const leverageFixed = Math.min(0.99, Math.max(0.15, leverageScore)).toFixed(3);
      
      const isCritical = leverageFixed >= 0.80;
      document.getElementById('simLeverage').innerHTML = \`\${leverageFixed} <span class="\${isCritical ? 'text-rr-pink font-bold' : 'text-slate-400'}">(\${isCritical ? 'CRITICAL LEVERAGE' : 'MODERATE'})</span>\`;

      // Wicket value calculation
      let wVal = 6.0 + (20 - balls/6) * 0.35 + (10 - wkts) * 0.3;
      wVal = Math.min(14.5, Math.max(5.5, wVal)).toFixed(1);
      document.getElementById('simWicketVal').textContent = \`\${wVal} runs\`;

      // Recommendation
      let rec = '';
      if (balls <= 18 && runs >= 30) {
        rec = 'Deploy primary yorker weapon (Bumrah/Ellis) or power finisher (Russell/David). Win swing is >12% per ball.';
      } else if (balls > 36 && rrr > 9.5) {
        rec = 'Deploy spin neutralizer (Rajat Patidar) or wrist spin clamp (Hasaranga/Narine). Strike rotation critical.';
      } else {
        rec = 'Standard phase baseline deployment. Protect wickets while maintaining 8.0+ RPO.';
      }
      document.getElementById('simRecommendation').textContent = rec;
    }

    // ==========================================
    // TAB 3: COMPARATOR LOGIC
    // ==========================================
    function populateComparatorSelectors() {
      const selectA = document.getElementById('compPlayerA');
      const selectB = document.getElementById('compPlayerB');
      if (!selectA || !selectB) return;

      selectA.innerHTML = '';
      selectB.innerHTML = '';

      PLAYERS.forEach(p => {
        const optA = document.createElement('option');
        optA.value = p.id;
        optA.textContent = \`\${p.flag} \${p.name} (#\${p.rank} \${p.role}) - \${p.score >= 0 ? '+' : ''}\${p.score.toFixed(3)}\`;
        selectA.appendChild(optA);

        const optB = document.createElement('option');
        optB.value = p.id;
        optB.textContent = \`\${p.flag} \${p.name} (#\${p.rank} \${p.role}) - \${p.score >= 0 ? '+' : ''}\${p.score.toFixed(3)}\`;
        selectB.appendChild(optB);
      });

      // Default pair: Gill vs Gaikwad
      selectA.value = 6288;
      selectB.value = 6059;
    }

    function loadPresetComparison(preset) {
      if (preset === 'gill_gaikwad') {
        document.getElementById('compPlayerA').value = 6288;
        document.getElementById('compPlayerB').value = 6059;
      } else if (preset === 'bumrah_ellis') {
        document.getElementById('compPlayerA').value = 2933;
        document.getElementById('compPlayerB').value = 7920;
      }
      renderComparison();
    }

    function renderComparison() {
      const idA = parseInt(document.getElementById('compPlayerA').value);
      const idB = parseInt(document.getElementById('compPlayerB').value);
      const pA = PLAYERS.find(p => p.id === idA) || PLAYERS[0];
      const pB = PLAYERS.find(p => p.id === idB) || PLAYERS[1];

      renderCompCard('compCardA', pA, pB, '#E00070');
      renderCompCard('compCardB', pB, pA, '#38BDF8');
      renderRadarChart(pA, pB);

      // Render Verdict
      const scoreDiff = (pA.score - pB.score).toFixed(3);
      const verdictBox = document.getElementById('compVerdictBox');
      const higherFloor = pA.score >= pB.score ? pA : pB;
      const higherPeak = pA.pressureAbility >= pB.pressureAbility ? pA : pB;
      const higherUplift = pA.uplift >= pB.uplift ? pA : pB;

      verdictBox.innerHTML = \`
        <div class="font-bold text-white flex items-center justify-between">
          <span>Executive War Room Verdict</span>
          <span class="text-rr-gold font-mono font-bold">Δ Score: \${Math.abs(scoreDiff)}</span>
        </div>
        <p class="text-slate-300 text-[11px] mt-1">
          <strong>\${higherFloor.name}</strong> offers the superior statistical reliability floor (\${higherFloor.score >= 0 ? '+' : ''}\${higherFloor.score.toFixed(3)} Q0.10).
          <strong>\${higherUplift.name}</strong> provides higher clutch acceleration spike (+ \${higherUplift.uplift.toFixed(3)} uplift).
        </p>
      \`;
    }

    function renderCompCard(containerId, player, opponent, accent) {
      const el = document.getElementById(containerId);
      if (!el) return;

      const diffScore = (player.score - opponent.score).toFixed(3);
      const diffUplift = (player.uplift - opponent.uplift).toFixed(3);
      const diffBalls = player.balls - opponent.balls;

      el.innerHTML = \`
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <span class="text-2xl">\${player.flag}</span>
            <div>
              <h3 class="font-bold text-base text-white">\${player.name}</h3>
              <span class="text-xs text-slate-400 font-mono">#\${player.rank} \${player.role} • \${player.team}</span>
            </div>
          </div>
          <span class="px-2.5 py-1 rounded-md font-mono font-bold text-xs bg-slate-800 text-white">₹\${player.auctionPrice} Cr</span>
        </div>

        <div class="grid grid-cols-2 gap-2 text-xs pt-2">
          <div class="p-2.5 rounded-lg bg-[#060D1A] border border-slate-800">
            <span class="text-[10px] text-slate-400 uppercase font-semibold">Q0.10 Score</span>
            <div class="font-mono text-base font-bold text-white mt-0.5">
              \${player.score >= 0 ? '+' : ''}\${player.score.toFixed(3)}
              <span class="text-[10px] \${diffScore >= 0 ? 'text-emerald-400' : 'text-rose-400'}">
                (\${diffScore >= 0 ? '+' : ''}\${diffScore})
              </span>
            </div>
          </div>

          <div class="p-2.5 rounded-lg bg-[#060D1A] border border-slate-800">
            <span class="text-[10px] text-slate-400 uppercase font-semibold">Clutch Uplift (Δ)</span>
            <div class="font-mono text-base font-bold text-emerald-400 mt-0.5">
              +\${player.uplift.toFixed(3)}
              <span class="text-[10px] \${diffUplift >= 0 ? 'text-emerald-400' : 'text-rose-400'}">
                (\${diffUplift >= 0 ? '+' : ''}\${diffUplift})
              </span>
            </div>
          </div>

          <div class="p-2.5 rounded-lg bg-[#060D1A] border border-slate-800">
            <span class="text-[10px] text-slate-400 uppercase font-semibold">Pressure Ability</span>
            <div class="font-mono text-sm font-bold text-white mt-0.5">+\${player.pressureAbility.toFixed(3)}</div>
          </div>

          <div class="p-2.5 rounded-lg bg-[#060D1A] border border-slate-800">
            <span class="text-[10px] text-slate-400 uppercase font-semibold">P(Δ > 0) Certainty</span>
            <div class="font-mono text-sm font-bold text-slate-200 mt-0.5">\${player.certainty.toFixed(1)}%</div>
          </div>
        </div>

        <div class="p-3 rounded-lg bg-[#060D1A] border border-slate-800 text-xs space-y-1">
          <div class="text-[10px] uppercase font-semibold text-slate-400">Scouting Verdict</div>
          <p class="text-slate-300 text-[11px] leading-relaxed">\${player.scouting}</p>
        </div>
      \`;
    }

    function renderRadarChart(pA, pB) {
      const ctx = document.getElementById('compRadarChart');
      if (!ctx) return;

      if (radarChart) radarChart.destroy();

      radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
          labels: ['Reliability Floor', 'Peak Ability', 'Clutch Uplift', 'Certainty', 'Sample Depth', 'Baseline Quality'],
          datasets: [
            {
              label: pA.name,
              data: pA.radar,
              backgroundColor: 'rgba(224, 0, 112, 0.25)',
              borderColor: '#E00070',
              borderWidth: 2,
              pointBackgroundColor: '#E00070',
              pointRadius: 3
            },
            {
              label: pB.name,
              data: pB.radar,
              backgroundColor: 'rgba(56, 189, 248, 0.25)',
              borderColor: '#38BDF8',
              borderWidth: 2,
              pointBackgroundColor: '#38BDF8',
              pointRadius: 3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: { color: '#E2E8F0', font: { size: 11 } }
            }
          },
          scales: {
            r: {
              angleLines: { color: 'rgba(148, 163, 184, 0.15)' },
              grid: { color: 'rgba(148, 163, 184, 0.15)' },
              pointLabels: { color: '#94A3B8', font: { size: 10, weight: 'bold' } },
              ticks: { display: false, min: 0, max: 100 }
            }
          }
        }
      });
    }

    // ==========================================
    // TAB 4: AUCTION WAR ROOM LOGIC
    // ==========================================
    function renderSquadSlots() {
      const container = document.getElementById('squadSlotsContainer');
      if (!container) return;

      container.innerHTML = '';
      let totalBudget = 0;
      let totalScore = 0;
      let overseasCount = 0;
      let filledCount = 0;

      Object.entries(squadSlots).forEach(([slotId, slot]) => {
        const p = slot.player;
        if (p) {
          totalBudget += p.auctionPrice;
          totalScore += p.score;
          if (p.isOverseas) overseasCount++;
          filledCount++;
        }

        const slotEl = document.createElement('div');
        slotEl.className = 'p-3.5 rounded-xl border border-slate-800 bg-[#060D1A] flex items-center justify-between gap-3 text-xs';

        if (p) {
          slotEl.innerHTML = \`
            <div class="flex items-center gap-2.5">
              <span class="text-xl">\${p.flag}</span>
              <div>
                <span class="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">\${slot.role}</span>
                <div class="font-bold text-white">\${p.name}</div>
                <div class="text-[10px] text-slate-400 font-mono">Q0.10: \${p.score >= 0 ? '+' : ''}\${p.score.toFixed(3)} • ₹\${p.auctionPrice} Cr</div>
              </div>
            </div>
            <button onclick="removeSquadSlot(\${slotId})" class="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-rose-400 transition-all">
              <i data-lucide="x" class="w-4 h-4"></i>
            </button>
          \`;
        } else {
          slotEl.innerHTML = \`
            <div>
              <span class="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Slot \${slotId}: \${slot.role}</span>
              <div class="font-semibold text-slate-500 italic mt-0.5">Unassigned Core Slot</div>
            </div>
            <button onclick="quickAssignSlot(\${slotId})" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-semibold text-[11px] transition-all">
              + Assign
            </button>
          \`;
        }

        container.appendChild(slotEl);
      });

      // Update Telemetry
      document.getElementById('squadCountDisplay').textContent = filledCount;
      document.getElementById('squadCountBadge').textContent = filledCount;
      document.getElementById('squadBudgetDisplay').textContent = totalBudget.toFixed(1);
      document.getElementById('squadScoreDisplay').textContent = (totalScore >= 0 ? '+' : '') + totalScore.toFixed(3);
      
      const ovEl = document.getElementById('squadOverseasDisplay');
      const ovStat = document.getElementById('overseasStatusText');
      ovEl.textContent = \`\${overseasCount} / 4\`;
      if (overseasCount > 4) {
        ovEl.className = 'text-2xl font-bold font-mono text-rose-500 mt-1';
        ovStat.textContent = '✗ Exceeds 4 Overseas IPL Limit!';
        ovStat.className = 'text-[10px] text-rose-400 font-bold mt-1';
      } else {
        ovEl.className = 'text-2xl font-bold font-mono text-emerald-400 mt-1';
        ovStat.textContent = '✓ Within IPL Quota';
        ovStat.className = 'text-[10px] text-emerald-400 font-semibold mt-1';
      }

      lucide.createIcons();
    }

    function togglePlayerInSquad(playerId) {
      const p = PLAYERS.find(x => x.id === playerId);
      if (!p) return;

      const existingSlotKey = Object.keys(squadSlots).find(k => squadSlots[k].player && squadSlots[k].player.id === playerId);
      if (existingSlotKey) {
        squadSlots[existingSlotKey].player = null;
        showToast(\`Removed \${p.name} from squad.\`);
      } else {
        // Find empty slot
        const emptyKey = Object.keys(squadSlots).find(k => !squadSlots[k].player);
        if (emptyKey) {
          squadSlots[emptyKey].player = p;
          showToast(\`Drafted \${p.name} into Slot \${emptyKey} (\${squadSlots[emptyKey].role})\`);
        } else {
          showToast('Squad is full! Remove a player first.', true);
        }
      }

      renderSquadSlots();
      renderTable();
    }

    function removeSquadSlot(slotId) {
      if (squadSlots[slotId]) {
        squadSlots[slotId].player = null;
        renderSquadSlots();
        renderTable();
      }
    }

    function quickAssignSlot(slotId) {
      // Pick best unassigned matching player
      const assignedIds = Object.values(squadSlots).filter(s => s.player).map(s => s.player.id);
      const candidate = PLAYERS.find(p => !assignedIds.includes(p.id));
      if (candidate) {
        squadSlots[slotId].player = candidate;
        renderSquadSlots();
        renderTable();
        showToast(\`Assigned \${candidate.name} to Slot \${slotId}\`);
      }
    }

    function loadSquadPreset(type) {
      clearSquad();
      if (type === 'fortress') {
        // Bumrah, Ellis, Narine, Gill, Patidar, Russell
        squadSlots[1].player = PLAYERS.find(p => p.id === 6288); // Gill
        squadSlots[2].player = PLAYERS.find(p => p.id === 5039); // Patidar
        squadSlots[3].player = PLAYERS.find(p => p.id === 1318); // Russell
        squadSlots[4].player = PLAYERS.find(p => p.id === 781);  // Narine
        squadSlots[5].player = PLAYERS.find(p => p.id === 7920); // Ellis
        squadSlots[6].player = PLAYERS.find(p => p.id === 2933); // Bumrah
        showToast('Loaded Preset: Fortress Defense');
      } else if (type === 'power') {
        // Gaikwad, Surya, David, Rauf, Hasaranga, Pathirana
        squadSlots[1].player = PLAYERS.find(p => p.id === 6059); // Gaikwad
        squadSlots[2].player = PLAYERS.find(p => p.id === 1699); // Surya
        squadSlots[3].player = PLAYERS.find(p => p.id === 6396); // David
        squadSlots[4].player = PLAYERS.find(p => p.id === 7364); // Rauf
        squadSlots[5].player = PLAYERS.find(p => p.id === 4900); // Hasaranga
        squadSlots[6].player = PLAYERS.find(p => p.id === 8661); // Pathirana
        showToast('Loaded Preset: Max Power Chase');
      } else if (type === 'domestic') {
        // Gill, Gaikwad, Patidar, Tilak, Harshal, Bumrah
        squadSlots[1].player = PLAYERS.find(p => p.id === 6288); // Gill
        squadSlots[2].player = PLAYERS.find(p => p.id === 6059); // Gaikwad
        squadSlots[3].player = PLAYERS.find(p => p.id === 5039); // Patidar
        squadSlots[4].player = PLAYERS.find(p => p.id === 7897); // Tilak
        squadSlots[5].player = PLAYERS.find(p => p.id === 2261); // Harshal
        squadSlots[6].player = PLAYERS.find(p => p.id === 2933); // Bumrah
        showToast('Loaded Preset: Indian Spine');
      }
      renderSquadSlots();
      renderTable();
    }

    function clearSquad() {
      Object.keys(squadSlots).forEach(k => squadSlots[k].player = null);
      renderSquadSlots();
      renderTable();
    }

    // ==========================================
    // TAB 5: HOLDOUT EVALUATION CHART
    // ==========================================
    function initHoldoutChart() {
      const ctx = document.getElementById('holdoutBarChart');
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
              backgroundColor: '#64748B',
              borderRadius: 6
            },
            {
              label: 'RR Model A+ (GBDT + Bayes)',
              data: [1.3688, 0.9131],
              backgroundColor: '#E00070',
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: { color: '#E2E8F0', font: { size: 11, weight: 'bold' } }
            },
            tooltip: {
              callbacks: {
                afterLabel: (ctx) => {
                  if (ctx.datasetIndex === 1) {
                    return ctx.dataIndex === 0 ? '-19.3% Prediction Error' : '-15.1% Prediction Error';
                  }
                  return '';
                }
              }
            }
          },
          scales: {
            y: {
              title: { display: true, text: 'Root Mean Squared Error (Lower is Better)', color: '#94A3B8' },
              grid: { color: 'rgba(148, 163, 184, 0.1)' },
              ticks: { color: '#94A3B8' },
              min: 0.5
            },
            x: {
              grid: { display: false },
              ticks: { color: '#E2E8F0', font: { weight: 'bold' } }
            }
          }
        }
      });
    }

    // ==========================================
    // PLAYER DEEP-DIVE SLIDE-OVER DRAWER
    // ==========================================
    function openPlayerDrawer(playerId) {
      const p = PLAYERS.find(x => x.id === playerId);
      if (!p) return;

      activePlayerDrawer = p;

      document.getElementById('drawerPlayerName').innerHTML = \`\${p.flag} \${p.name}\`;
      document.getElementById('drawerPlayerMeta').textContent = \`#\${p.rank} \${p.role} • \${p.team} • ID: \${p.id}\`;
      document.getElementById('drawerAvatar').textContent = p.name.split(' ').map(n=>n[0]).join('').slice(0,2);
      document.getElementById('drawerAvatar').className = \`w-11 h-11 rounded-lg flex items-center justify-center font-bold text-lg shadow-md \${p.role === 'Batter' ? 'bg-rr-pink text-white' : 'bg-sky-500 text-white'}\`;

      document.getElementById('drawerScore').textContent = (p.score >= 0 ? '+' : '') + p.score.toFixed(3);
      document.getElementById('drawerUplift').textContent = (p.uplift >= 0 ? '+' : '') + p.uplift.toFixed(3);
      document.getElementById('drawerCertainty').textContent = \`\${p.certainty.toFixed(1)}% Cert.\`;
      document.getElementById('drawerBalls').textContent = p.balls;
      document.getElementById('drawerMatches').textContent = \`\${p.matches} matches\`;

      document.getElementById('drawerPP').textContent = p.phaseSplit.powerplay;
      document.getElementById('drawerMid').textContent = p.phaseSplit.middle;
      document.getElementById('drawerDeath').textContent = p.phaseSplit.death;

      document.getElementById('drawerScouting').textContent = p.scouting;

      const inSquad = Object.values(squadSlots).some(s => s.player && s.player.id === p.id);
      const squadBtn = document.getElementById('drawerAddSquadBtn');
      squadBtn.innerHTML = inSquad ? 
        '<i data-lucide="check" class="w-4 h-4"></i> Remove from Rajasthan Royals Target Core' : 
        '<i data-lucide="plus-circle" class="w-4 h-4"></i> Add to Rajasthan Royals Target Core';

      // Draw Bell Curve
      drawBellCurve(p);

      // Open drawer
      document.getElementById('playerDrawerOverlay').classList.remove('hidden');
      document.getElementById('playerDrawer').classList.remove('translate-x-full');

      lucide.createIcons();
    }

    function closePlayerDrawer() {
      document.getElementById('playerDrawerOverlay').classList.add('hidden');
      document.getElementById('playerDrawer').classList.add('translate-x-full');
      activePlayerDrawer = null;
    }

    function togglePlayerInSquadFromDrawer() {
      if (activePlayerDrawer) {
        togglePlayerInSquad(activePlayerDrawer.id);
        const inSquad = Object.values(squadSlots).some(s => s.player && s.player.id === activePlayerDrawer.id);
        const squadBtn = document.getElementById('drawerAddSquadBtn');
        squadBtn.innerHTML = inSquad ? 
          '<i data-lucide="check" class="w-4 h-4"></i> Remove from Rajasthan Royals Target Core' : 
          '<i data-lucide="plus-circle" class="w-4 h-4"></i> Add to Rajasthan Royals Target Core';
        lucide.createIcons();
      }
    }

    // HTML5 Canvas Bayesian Normal Distribution Curve
    function drawBellCurve(player) {
      const canvas = document.getElementById('bellCurveCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.width;
      const h = canvas.height;

      ctx.clearRect(0, 0, w, h);

      // Parameters
      const mu = player.pressureAbility;
      const q10 = player.score;
      const sigma = (mu - q10) / 1.282;

      // Range for x: mu - 3.5 sigma to mu + 3.5 sigma
      const xMin = mu - 3.2 * sigma;
      const xMax = mu + 3.2 * sigma;

      function toX(xVal) {
        return ((xVal - xMin) / (xMax - xMin)) * (w - 40) + 20;
      }

      function normalPdf(x) {
        return (1 / (sigma * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - mu) / sigma, 2));
      }

      const maxPdf = normalPdf(mu);
      function toY(pdfVal) {
        return h - 25 - (pdfVal / maxPdf) * (h - 45);
      }

      // Draw 90% shaded credible region (from q10 to xMax)
      ctx.beginPath();
      ctx.moveTo(toX(q10), toY(0));
      for (let x = q10; x <= xMax; x += (xMax - q10) / 40) {
        ctx.lineTo(toX(x), toY(normalPdf(x)));
      }
      ctx.lineTo(toX(xMax), toY(0));
      ctx.closePath();
      ctx.fillStyle = 'rgba(224, 0, 112, 0.18)';
      ctx.fill();

      // Draw full normal curve line
      ctx.beginPath();
      for (let x = xMin; x <= xMax; x += (xMax - xMin) / 80) {
        const px = toX(x);
        const py = toY(normalPdf(x));
        if (x === xMin) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.strokeStyle = '#38BDF8';
      ctx.lineWidth = 2.5;
      ctx.stroke();

      // Draw Q0.10 vertical marker
      const qX = toX(q10);
      ctx.beginPath();
      ctx.moveTo(qX, 10);
      ctx.lineTo(qX, h - 20);
      ctx.strokeStyle = '#E00070';
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);

      // Draw Mean vertical marker
      const muX = toX(mu);
      ctx.beginPath();
      ctx.moveTo(muX, 15);
      ctx.lineTo(muX, h - 20);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Labels
      ctx.fillStyle = '#E00070';
      ctx.font = 'bold 10px Consolas, monospace';
      ctx.fillText(\`Q0.10: \${q10 >= 0 ? '+' : ''}\${q10.toFixed(3)}\`, Math.max(10, qX - 45), 18);

      ctx.fillStyle = '#94A3B8';
      ctx.font = '10px Consolas, monospace';
      ctx.fillText(\`Mean: +\${mu.toFixed(3)}\`, Math.min(w - 75, muX + 6), 30);

      // Baseline line
      ctx.beginPath();
      ctx.moveTo(10, h - 20);
      ctx.lineTo(w - 10, h - 20);
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.3)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // ==========================================
    // TOAST & SHORTCUTS HELPERS
    // ==========================================
    function showToast(message, isError = false) {
      const container = document.getElementById('toastContainer');
      const toast = document.createElement('div');
      toast.className = \`px-4 py-2.5 rounded-lg text-xs font-semibold text-white shadow-2xl flex items-center gap-2 transform transition-all duration-300 pointer-events-auto \${isError ? 'bg-rose-600' : 'bg-slate-900 border border-slate-700'}\`;
      toast.innerHTML = \`<i data-lucide="\${isError ? 'alert-triangle' : 'check-circle'}" class="w-4 h-4 text-emerald-400"></i> \${message}\`;
      
      container.appendChild(toast);
      lucide.createIcons();

      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
      }, 3000);
    }

    function setupKeyboardShortcuts() {
      // Shortcuts modal
      document.getElementById('shortcutsBtn').addEventListener('click', () => {
        document.getElementById('shortcutsModal').showModal();
      });

      // Export menu toggle
      const exportBtn = document.getElementById('exportDropdownBtn');
      const exportMenu = document.getElementById('exportMenu');
      exportBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        exportMenu.classList.toggle('hidden');
      });
      document.addEventListener('click', () => exportMenu.classList.add('hidden'));

      // Keyboard events
      document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
          if (e.key === 'Escape') {
            e.target.blur();
            closePlayerDrawer();
          }
          return;
        }

        if (e.key === '/') {
          e.preventDefault();
          document.getElementById('searchInput').focus();
        } else if (e.key === 'Escape') {
          closePlayerDrawer();
          const modal = document.getElementById('shortcutsModal');
          if (modal.open) modal.close();
        } else if (e.key === 't' || e.key === 'T') {
          toggleTheme();
        } else if (e.key === '?') {
          document.getElementById('shortcutsModal').showModal();
        } else if (e.key >= '1' && e.key <= '5') {
          const tabMap = { '1': 'leaderboard', '2': 'quadrant', '3': 'comparator', '4': 'warroom', '5': 'diagnostics' };
          switchTab(tabMap[e.key]);
        }
      });
    }

    // Export CSV
    function exportCSV() {
      let csv = 'rank,role,player_name,nationality,conservative_score,pressure_ability,normal_ability,uplift,prob_positive_uplift,pressure_balls,pressure_matches\\n';
      PLAYERS.forEach(p => {
        csv += \`\${p.rank},\${p.role},"\${p.name}",\${p.nationality},\${p.score},\${p.pressureAbility},\${p.normalAbility},\${p.uplift},\${p.certainty}%,\${p.balls},\${p.matches}\\n\`;
      });

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'rajasthan_royals_superr_selector_rankings.csv';
      a.click();
      URL.revokeObjectURL(url);
      showToast('Exported rankings to CSV');
    }

    // Export JSON
    function exportJSON() {
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(PLAYERS, null, 2));
      const a = document.createElement('a');
      a.href = dataStr;
      a.download = 'rajasthan_royals_superr_selector_rankings.json';
      a.click();
      showToast('Exported rankings to JSON');
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
