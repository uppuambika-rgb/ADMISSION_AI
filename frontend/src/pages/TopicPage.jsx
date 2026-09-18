import React from 'react';
import { useParams, useNavigate, useSearchParams, Link } from 'react-router-dom';
import { IMAGES } from '../assets/images';

// Topic content components
import RankAnalysis from './topics/RankAnalysis';
import CollegePredictor from './topics/CollegePredictor';
import CollegeInfo from './topics/CollegeInfo';
import BranchExplorer from './topics/BranchExplorer';
import FeesScholarships from './topics/FeesScholarships';
import HostelFacilities from './topics/HostelFacilities';
import Placements from './topics/Placements';
import ChoiceFilling from './topics/ChoiceFilling';
import AICounsellor from './topics/AICounsellor';

const TOPIC_META = {
  'rank-analysis': {
    icon: '📊',
    title: 'Rank Analysis',
    desc: 'Know your chances in top colleges based on your rank and category across all tiers.',
    bg: IMAGES.rankAnalysis,
    component: <RankAnalysis />,
  },
  'college-predictor': {
    icon: '🎓',
    title: 'College Predictor',
    desc: 'Get personalized college recommendations based on your rank, category and preferred branch.',
    bg: IMAGES.collegePredictor,
    // component rendered separately — needs search params
  },
  'college-info': {
    icon: '🏛️',
    title: 'College Information',
    desc: 'Detailed information about colleges, courses, cutoffs and campus facilities.',
    bg: IMAGES.collegeInfo,
    component: <CollegeInfo />,
  },
  'branch-explorer': {
    icon: '🔀',
    title: 'Branch Explorer',
    desc: 'Explore branches, career scope, curriculum highlights and top recruiters.',
    bg: IMAGES.branchExplorer,
    component: <BranchExplorer />,
  },
  'fees': {
    icon: '💰',
    title: 'Fees & Scholarships',
    desc: 'Compare annual fees across colleges and discover scholarships and financial aid.',
    bg: IMAGES.fees,
    component: <FeesScholarships />,
  },
  'hostel': {
    icon: '🏠',
    title: 'Hostel & Facilities',
    desc: 'Check hostel availability, mess, labs, sports, transport and campus life details.',
    bg: IMAGES.hostel,
    component: <HostelFacilities />,
  },
  'placements': {
    icon: '💼',
    title: 'Placements',
    desc: 'View placement statistics, median CTCs, placement rates and top recruiters.',
    bg: IMAGES.placements,
    component: <Placements />,
  },
  'choice-filling': {
    icon: '📋',
    title: 'Choice Filling',
    desc: 'Get expert help creating an optimised preference list for JoSAA / CSAB counselling.',
    bg: IMAGES.choiceFilling,
    component: <ChoiceFilling />,
  },
  'ai-counsellor': {
    icon: '🤖',
    title: 'AI Counsellor',
    desc: 'Ask anything and get instant, personalised guidance for all your admission queries.',
    bg: IMAGES.aiCounsellor,
    component: <AICounsellor />,
  },
};

export default function TopicPage() {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const meta = TOPIC_META[topicId];

  if (!meta) {
    return (
      <div className="topic-not-found">
        <h2>Topic not found</h2>
        <button className="back-btn" onClick={() => navigate('/')}>← Back to Dashboard</button>
      </div>
    );
  }

  // CollegePredictor needs URL params from hero form
  const component =
    topicId === 'college-predictor' ? (
      <CollegePredictor
        initialExam={searchParams.get('exam') || 'JEE Main'}
        initialRank={searchParams.get('rank') || ''}
        initialCategory={searchParams.get('category') || 'General'}
        initialBranch={searchParams.get('branch') || 'Computer Science & Engineering'}
      />
    ) : (
      meta.component
    );

  return (
    <div className="topic-page">
      {/* Hero */}
      <section
        className="topic-hero"
        style={{ backgroundImage: `url(${meta.bg})` }}
        aria-label={`${meta.title} hero section`}
      >
        <div className="topic-hero-overlay" aria-hidden="true"></div>
        <div className="topic-hero-content">
          <Link to="/" className="back-btn" aria-label="Back to Dashboard">
            ← Back to Dashboard
          </Link>
          <div className="topic-hero-icon" aria-hidden="true">{meta.icon}</div>
          <h1 className="topic-hero-title">{meta.title}</h1>
          <p className="topic-hero-desc">{meta.desc}</p>
        </div>
      </section>

      {/* Content */}
      <div className="topic-body">
        {component}
      </div>
    </div>
  );
}
