export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://staging-solomon-api.beusable.net'
export const BEUSABLE_BASE_URL = import.meta.env.VITE_BEUSABLE_API_BASE_URL || 'https://staging-api.beusable.net'
export const HUB_BASE_URL = import.meta.env.VITE_API_HUB_BASE_URL || 'https://staging-api-hub.beusable.net'

export const BEUSABLE_HOME_URL = import.meta.env.VITE_BEUSABLE_HOME_URL || 'https://staging-new-home.beusable.net'
export const BA_URL = import.meta.env.VITE_BA_URL || 'https://staging-analytics.beusable.net'

export const themes = [
  {
    name: 'default',
    colorCodes: ['#ec0047', '#e5476e', '#f8eaf0', '#fff']
  },
  {
    name: 'red',
    colorCodes: ['#e60000', '#e90c0c', '#f8edea', '#fff']
  },
  {
    name: 'orange',
    colorCodes: ['#c15f3c', '#c15f3c', '#f4f3ee', '#fff']
  },
  {
    name: 'yellow',
    colorCodes: ['#fbc000', '#fabc20', '#f8f7ea', '#fff']
  },
  {
    name: 'green',
    colorCodes: ['#21b600', '#43c218', '#ecf8ea', '#fff']
  },
  {
    name: 'blue',
    colorCodes: ['#00b2f3', '#00b2f3', '#f3f3f3', '#fff']
  },
  {
    name: 'black',
    colorCodes: ['#000', '#79797f', '#f3f3f3', '#fff']
  },
  {
    name: 'darkblue',
    colorCodes: ['#1b345b', '#15356b', '#2f4b79', '#5578b2']
  },
  {
    name: 'dark',
    colorCodes: ['#000', '#474747', '#626262', '#878787']
  }
]

export const AGENT = {
  MAIN: 'main',
  CS: 'cs',
  VOC: 'voc',
  AB_TEST: 'ab-test',
  SCROLL: 'scroll',
  SCROLL_CHAT: 'scrollChat',
  REPORT_CHAT: 'reportchat',
  JOURNEYMAP_MCP: 'journeymapMCP',
  CX_DATA_TREND_MCP: 'cxDataTrendMCP',
  DASHBOARD: 'dashboard',
  DASHBOARD_HELL: 'dashboardHell',
  DASHBOARD_GA: 'dashboardGa',
  DASHBOARD_CHAT: 'dashboardChat',
  SCHEMA_JSON: 'schemaJSON',
  SCHEMA_SIMPLE: 'schemaSimple',
  SCHEMA_CHAT: 'schemaChat',
  WHITE_PAPER: 'whitePaper',
  CX_TRENDS: 'cxTrends'
}

export const agentMeta = {
  [AGENT.MAIN]: {
    options: ['model']
  },
  [AGENT.CS]: {
    options: ['model']
  },
  [AGENT.VOC]: {
    isIdAvailable: true,
    options: ['model']
  },
  [AGENT.AB_TEST]: {
    isJsonAvailable: true,
    options: ['model', 'lang']
  },
  [AGENT.SCROLL]: {
    isJsonAvailable: true,
    options: ['model', 'lang']
  },
  [AGENT.SCROLL_CHAT]: {
    isIdAvailable: true,
    isReportChat: true,
    serviceType: 'beusable',
    options: ['model']
  },
  [AGENT.REPORT_CHAT]: {
    isIdAvailable: true,
    isReportChat: true,
    serviceType: 'ba',
    options: ['model']
  },
  [AGENT.JOURNEYMAP_MCP]: {
    isMCP: true,
    agent: 'journeymapMCP',
    options: ['model']
  },
  [AGENT.CX_DATA_TREND_MCP]: {
    isMCP: true,
    agent: 'cxDataTrendMCP',
    options: ['model']
  },
  [AGENT.DASHBOARD]: {
    options: ['model']
  },
  [AGENT.DASHBOARD_HELL]: {
    options: ['model']
  },
  [AGENT.DASHBOARD_GA]: {
    options: ['model']
  },
  [AGENT.DASHBOARD_CHAT]: {
    isIdAvailable: true,
    isReportChat: true,
    serviceType: 'ba',
    options: ['model']
  },
  [AGENT.SCHEMA_JSON]: {
    isMCP: true,
    agent: 'schemaJSON',
    isJsonAvailable: true,
    options: ['model']
  },
  [AGENT.SCHEMA_SIMPLE]: {
    isMCP: true,
    agent: 'schemaSimple',
    options: ['model']
  },
  [AGENT.SCHEMA_CHAT]: {
    isIdAvailable: true,
    isReportChat: true,
    serviceType: 'geo',
    options: ['model']
  },
  [AGENT.WHITE_PAPER]: {
    isIdAvailable: true,
    isReportChat: true,
    serviceType: 'geo',
    options: ['model']
  },
  [AGENT.CX_TRENDS]: {
    isIdAvailable: true,
    isReportChat: true,
    serviceType: 'geo',
    options: ['model']
  }
}

export const DEFAULT_TYPE = '전체'

export const WELCOME_MESSAGE = {
  main: `안녕하세요, UX GPT입니다!\n뷰저블 서비스, 데이터 분석에 관한 궁금증이 있으시다면,\n저에게 질문해주세요 🥰`,
  cs: `안녕하세요, UX GPT for CS입니다!\n뷰저블 서비스, 데이터 분석에 관한 궁금증이 있으시다면,\n저에게 질문해주세요 🥰`,
}

export const askAgent = {
  wireTransferPayment: '무통장 결제 방법',
  plansAndCharging: '서비스 플랜 및 충전',
  features: '서비스 기능',
  installation: '코드 설치',
  dataCollection: '데이터 수집',
  partnersAndTutorial: '서비스 교육 및 파트너',
  others: ''
}

export const LANGS = {
  한국어: 'ko',
  영어: 'en',
  일본어: 'ja'
}

export const HISTORY_TAB = {
  result: '결과',
  prompt: '프롬프트',
  query: '파인콘',
  refer: '레퍼런스'
}

export const COMPARE_SINGLE = 1
export const COMPARE_DUAL = 2
export const VERSION_SELECTED = 'selected'
export const VERSION_COMPARED = 'compared'

export const AI_CATEGORY = {
  primary: {
    ecommerce: {
      icon: 'icon-legacy-category-ecommerce',
      title: {
        ko: '이커머스&리테일테크',
        en: 'ecommerce',
        ja: 'ECサイト'
      },
      description: {
        ko: '구매와 관련된 여정과 페이지들을 중점으로 분석해볼 수 있습니다. ',
        en: 'It is necessary to focus on analyzing the purchase journey and pages related to the purchase.',
        ja: '購入カスタマージャーニーと関連あるページを分析できます。'
      }
    },
    finance: {
      icon: 'icon-legacy-category-finance',
      title: {
        ko: '핀테크&디지털금융',
        en: 'finance',
        ja: '金融・ファイナンス'
      },
      description: {
        ko: '서비스의 정확한 정보를 쉽게 얻을 수 있어야 합니다.',
        en: 'It should be easy to obtain accurate information about the service.',
        ja: 'サービスの正確な情報を取得できるようにしましょう。'
      }
    },
    entertainment: {
      icon: 'icon-legacy-category-entertainment',
      title: {
        ko: '미디어&엔터테인먼트테크',
        en: 'entertainment',
        ja: 'エンタメ・メディア'
      },
      description: {
        ko: '사용자들이 관심있는 정보를 다양하게 탐색하고 흥미를 느낄 수 있어야 합니다.',
        en: 'Users should be able to explore a variety of information of interest and find interest in it.',
        ja: 'カスタマーが興味・関心を持つ情報を検索できるようにしましょう。'
      }
    },
    mobility: {
      icon: 'icon-legacy-category-mobility',
      title: {
        ko: '온디맨드&모빌리티',
        en: 'mobility',
        ja: '動画配信&モビリティサービス'
      },
      description: {
        ko: '사용자들이 관심있는 정보를 다양하게 탐색하고 원하는 정보를 얻을 수 있어야 합니다.',
        en: 'Users should be able to explore a variety of information of interest and obtain the information they want.',
        ja: 'カスタマーが興味・関心を持つ情報を検索できるようにしましょう。'
      }
    },
    health: {
      icon: 'icon-legacy-category-health',
      title: {
        ko: '디지털헬스케어',
        en: 'health',
        ja: 'デジタルヘルスケア'
      },
      description: {
        ko: '사용자들이 관심있는 정보를 다양하게 탐색하고 원하는 정보를 얻을 수 있어야 합니다.',
        en: 'Users should be able to explore a variety of information of interest and obtain the information they want.',
        ja: 'カスタマーが興味・関心を持つ情報を検索できるようにしましょう。'
      }
    },
    education: {
      icon: 'icon-legacy-category-education',
      title: {
        ko: '에듀테크',
        en: 'education',
        ja: 'eラーニング'
      },
      description: {
        ko: '사용자들이 다양한 정보들을 쉽게 탐색해서 관심있는 콘텐츠까지 도달할 수 있어야 합니다. ',
        en: 'Users should be able to easily navigate through various information and reach content of interest.',
        ja: 'カスタマーが多様な情報を検索し、興味あるコンテンツにたどり着けるようにしましょう。'
      }
    },
    agency: {
      icon: 'icon-legacy-category-agency',
      title: {
        ko: '디지털에이전시&LaaS',
        en: 'agency',
        ja: '広告・マーケティング代理店'
      },
      description: {
        ko: '서비스의 브랜딩이 잘 전달되고, 다양한 정보들을 쉽게 탐색할 수 있어야 합니다. ',
        en: 'The branding of the service should be clearly visible, and various information should be easily navigable.',
        ja: 'サービスブランディングが正確に認知され、多様な情報を検索できるようにしましょう。'
      }
    },
    government: {
      icon: 'icon-legacy-category-government',
      title: {
        ko: '공공복지&행정서비스',
        en: 'government',
        ja: '行政サービス'
      },
      description: {
        ko: '사용자들이 원하는 목표를 쉽고 빠르게 달성할 수 있어야 합니다.',
        en: 'Users should be able to achieve their desired goals easily and quickly.',
        ja: '簡単にわかりやすく、カスタマーが訪問した目的を達成できるようにしましょう。'
      }
    },
    'Public Services': {
      value: 'Public Services',
      icon: 'icon-category-public',
      title: {
        ko: '공공',
        en: 'Public Services',
        ja: '公共サービス'
      },
      description: {
        ko: '사용자 편의를 최우선으로 하여 명확하고 접근 가능한 정보 구조를 제공해야 합니다.',
        en: 'The information structure must prioritize user convenience by being clear and easily accessible.',
        ja: 'ユーザーの利便性を最優先し、明確でアクセスしやすい情報構造を提供しましょう。'
      },
      subCategories: ['Public Services', 'Institutions/Organizations', 'Government Administration']
    },
    Education: {
      value: 'Education',
      icon: 'icon-category-education',
      title: {
        ko: '교육',
        en: 'Education',
        ja: '教育'
      },
      description: {
        ko: '학습자 중심의 간편한 콘텐츠 접근성과 인터랙티브한 학습 환경을 지원해야 합니다.',
        en: 'Ensure easy access to content and support an interactive learning environment centered on learners.',
        ja: '学習者がコンテンツにアクセスしやすく、インタラクティブな学習環境を提供しましょう。'
      },
      subCategories: ['Early Education', 'Childcare Education', 'Professional Training', 'Schools']
    },
    Finance: {
      value: 'Finance',
      icon: 'icon-category-finance',
      title: {
        ko: '금융',
        en: 'Finance',
        ja: '金融'
      },
      description: {
        ko: '보안성과 신뢰를 바탕으로 쉬운 금융 거래와 정보 확인 과정을 제공해야 합니다.',
        en: 'Offer secure and trustworthy financial transactions and streamlined information verification processes.',
        ja: 'セキュリティと信頼性を基盤に、簡単な金融取引と情報確認のプロセスを提供しましょう。'
      },
      subCategories: [
        'Financial Tools',
        'Insurance',
        'Credit',
        'Banking',
        'Wealth Management',
        'Investments'
      ]
    },
    Technology: {
      value: 'Technology',
      icon: 'icon-category-technology',
      title: {
        ko: '기술',
        en: 'Technology',
        ja: '技術'
      },
      description: {
        ko: '기술적 전문성을 효과적으로 전달하면서 사용자 친화적인 인터페이스를 구현해야 합니다.',
        en: 'Deliver technical expertise effectively while implementing user-friendly interfaces.',
        ja: '技術的な専門性を効果的に伝えつつ、ユーザーフレンドリーなインターフェースを実現しましょう。'
      },
      subCategories: [
        'Construction',
        'Engineering',
        'Materials/Chemicals',
        'Energy',
        'Aerospace/Aviation',
        'Manufacturing',
        'Maritime/Shipping',
        'ESG'
      ]
    },
    Leisure: {
      value: 'Leisure',
      icon: 'icon-category-leisure',
      title: {
        ko: '레저',
        en: 'Leisure',
        ja: 'レジャー'
      },
      description: {
        ko: '감각적인 콘텐츠와 예약 및 구매의 간소화를 통해 사용자의 흥미를 유도해야 합니다.',
        en: 'Encourage user interest by simplifying content, reservations, and purchasing processes.',
        ja: '予約・購入プロセスを簡略化し、魅力的なコンテンツでユーザーの関心を引きつけましょう。'
      },
      subCategories: ['Sports', 'Travel/Tourism', 'Hotels/Resorts']
    },
    Retail: {
      value: 'Retail',
      icon: 'icon-category-retail',
      title: {
        ko: '리테일',
        en: 'Retail',
        ja: '小売'
      },
      description: {
        ko: '직관적인 제품 탐색과 원활한 결제 프로세스를 통해 구매 경험을 향상시켜야 합니다.',
        en: 'Improve the purchase experience through intuitive product navigation and a seamless payment process.',
        ja: '直感的な商品探索とスムーズな決済プロセスを提供し、購入体験を向上させましょう。'
      },
      subCategories: [
        'Furniture',
        'Health/Wellness',
        'Shared Services',
        'Beauty',
        'Household Goods',
        'Food/Beverage',
        'E-Commerce',
        'Distribution',
        'Electronics',
        'Fashion',
        'Franchises'
      ]
    },
    'Consumption/Lifestyle': {
      value: 'Consumption/Lifestyle',
      icon: 'icon-category-retail',
      description: {
        ko: '직관적인 제품 탐색과 원활한 결제 프로세스를 통해 구매 경험을 향상시켜야 합니다.',
        en: 'Improve the purchase experience through intuitive product navigation and a seamless payment process.',
        ja: '直感的な商品探索とスムーズな決済プロセスを提供し、購入体験を向上させましょう。'
      }
    },
    Entertainment: {
      value: 'Entertainment',
      icon: 'icon-category-entertainment',
      title: {
        ko: '엔터',
        en: 'Entertainment',
        ja: 'エンターテイメント'
      },
      description: {
        ko: '몰입감을 높이는 시각적 디자인과 사용자의 즐길 거리를 쉽게 찾을 수 있도록 설계해야 합니다.',
        en: 'Design visual elements that enhance engagement and make it easy for users to find enjoyable content.',
        ja: '視覚的に楽しめるデザインを採用し、ユーザーがコンテンツを見つけやすいようにしましょう。'
      },
      subCategories: [
        'Games',
        'Digital Content',
        'Media/News',
        'Films',
        'Arts',
        'Exhibitions/Performances'
      ]
    },
    Healthcare: {
      value: 'Healthcare',
      icon: 'icon-category-health',
      title: {
        ko: '의료',
        en: 'Healthcare',
        ja: '医療'
      },
      description: {
        ko: '신뢰감을 줄 수 있도록 정확하고 직관적인 진료 및 예약 정보를 제공해야 합니다.',
        en: 'Provide accurate and intuitive medical consultation and reservation details to build trust.',
        ja: 'ユーザーに信頼感を与えるために、正確で直感的な診療・予約情報を提供しましょう。'
      },
      subCategories: [
        'Healthcare Services',
        'Specialized Healthcare',
        'Pharmaceuticals',
        'Comprehensive Healthcare'
      ]
    },
    Information: {
      value: 'Information',
      icon: 'icon-category-information',
      title: {
        ko: '정보',
        en: 'Information',
        ja: '情報'
      },
      description: {
        ko: '복잡한 데이터를 명확하게 시각화하고, 필요한 정보를 빠르게 검색할 수 있어야 합니다.',
        en: 'Visualize complex data clearly and enable users to quickly search for necessary information.',
        ja: '複雑なデータを視覚化し、必要な情報を素早く検索できるようにしましょう。'
      },
      subCategories: ['Books', 'Real Estate', 'Expert Insights', 'Jobs', 'Communities']
    },
    IT: {
      value: 'IT',
      icon: 'icon-category-it',
      title: {
        ko: 'IT',
        en: 'IT',
        ja: 'IT'
      },
      description: {
        ko: '복잡한 기술 정보를 쉽게 이해할 수 있도록 설명과 탐색 과정을 최적화해야 합니다.',
        en: 'Optimize explanations and navigation to help users easily understand complex technical information.',
        ja: '複雑な技術情報を理解しやすくするため、説明と探索プロセスを最適化しましょう。'
      },
      subCategories: ['Mobility', 'Telecommunications', 'IT Solutions']
    }
  },
  secondaryGroup: [
    {
      title: {
        ko: '주문',
        en: 'Order',
        ja: '注文'
      },
      children: ['order', 'payment', 'cart']
    },
    {
      title: {
        ko: '신청',
        en: 'Request',
        ja: '申請'
      },
      children: ['purchase', 'support']
    },
    {
      title: {
        ko: '회원',
        en: 'Member',
        ja: '会員'
      },
      children: ['loginpage', 'mypage', 'signin']
    },
    {
      title: {
        ko: '정보',
        en: 'Info',
        ja: '情報'
      },
      children: ['pricing', 'event', 'detail']
    },
    {
      title: {
        ko: '탐색',
        en: 'Search',
        ja: '探索'
      },
      children: ['recruit', 'list', 'main']
    }
  ],
  secondary: {
    order: {
      title: {
        ko: '주문 관련 정보',
        en: 'Order',
        ja: '注文ページ'
      },
      description: {
        ko: '정확한 주문 정보를 쉽고 빠르게 확인하고 관리할 수 있어야 해요.',
        en: 'users should be able to easily and quickly check and manage accurate order information.',
        ja: '正確な注文情報を簡単かつ迅速に確認し、管理できる必要があります。'
      },
      color: 'rgba(175, 240, 91, 1)'
    },
    payment: {
      title: {
        ko: '주문/결제정보/결제완료',
        en: 'Payment',
        ja: '決済ページ'
      },
      description: {
        ko: '원활한 구매 진행을 위해 필요한 서식 활용과 전환을 쉽게 할 수 있어야 해요.',
        en: 'users should be able to utilize forms and transition smoothly to ensure a seamless purchase process.',
        ja: '円滑な購入手続きを行うために必要なフォームの利用や転換が簡単にできる必要があります。'
      },
      color: 'rgb(208, 233, 108)'
    },
    cart: {
      title: {
        ko: '장바구니',
        en: 'Cart',
        ja: 'カートページ'
      },
      description: {
        ko: '구매를 원하는 상품들을 정확하게 확인하고, 구매 결정을 내리는데 도움을 얻을 수 있어야 해요.',
        en: 'users should be able to accurately review the products they want to purchase and get support in making purchasing decisions.',
        ja: '購入したい商品を正確に確認し、購入決定をサポートできる必要があります。'
      },
      color: 'rgb(250, 223, 79)'
    },
    purchase: {
      title: {
        ko: '서비스 신청',
        en: 'Purchase',
        ja: 'お申し込みページ'
      },
      description: {
        ko: '서비스를 신청하기 위해 요구하는 정보들을 간편하게 입력하고 확인할 수 있어야 해요.',
        en: 'users should be able to easily enter and verify the required information to apply for services.',
        ja: 'サービスを申請するために必要な情報を簡単に入力し、確認できる必要があります。'
      },
      color: 'rgb(149, 220, 220)'
    },
    support: {
      title: {
        ko: '고객센터/문의',
        en: 'Support',
        ja: 'お問い合わせページ'
      },
      description: {
        ko: '사용자의 문제를 해결하기 위한 정보를 쉽고 빠르게 찾을 수 있어야 해요.',
        en: 'users should be able to quickly and easily find information that solves their issues.',
        ja: 'ユーザーの問題を解決するための情報を簡単かつ迅速に見つけることができる必要があります。'
      },
      color: 'rgb(255, 175, 100)'
    },
    loginpage: {
      title: {
        ko: '로그인 이후',
        en: 'Personalization',
        ja: 'ログイン後のページ'
      },
      description: {
        ko: '고객에게 맞춤화 된 정보들을 정확하게 확인할 수 있어야 해요.',
        en: 'users should be able to accurately check personalized information tailored to them.',
        ja: 'ユーザーにカスタマイズされた情報を正確に確認できる必要があります。'
      },
      color: 'rgb(255, 122, 186)'
    },
    mypage: {
      title: {
        ko: '내 정보 확인/관리',
        en: 'My page',
        ja: 'マイページ'
      },
      description: {
        ko: '정확한 내 정보를 쉽고 빠르게 확인하고 관리할 수 있어야 해요.',
        en: 'users should be able to quickly and easily check and manage their personal information.',
        ja: '正確な個人情報を簡単かつ迅速に確認し、管理できる必要があります。'
      },
      color: 'rgb(255, 148, 148)'
    },
    signin: {
      title: {
        ko: '로그인/회원가입/로그인관련',
        en: 'Sign in',
        ja: 'ログインページ'
      },
      description: {
        ko: '개인화 콘텐츠로 빠르게 접근할 수 있도록 회원가입 또는 로그인을 쉽게 성공할 수 있어야 해요.',
        en: 'users should be able to easily sign up or log in to quickly access personalized content.',
        ja: '個人化されたコンテンツにすぐアクセスできるよう、簡単に会員登録やログインができる必要があります。'
      },
      color: 'rgb(253, 138, 255)'
    },
    pricing: {
      title: {
        ko: '상품/요금제 안내/가입',
        en: 'Pricing',
        ja: '料金ページ'
      },
      description: {
        ko: '다양한 상품이나 요금제가 안내되기 때문에 사용자들이 정보에 흥미를 갖고 잘 인지할 수 있도록 구성해야 해요.',
        en: "various products or plans are introduced, so it should be designed to grab users' interest and ensure they understand the information well.",
        ja: '様々な商品や料金プランが紹介されており、ユーザーが興味を持ち、情報をしっかりと認識できるように構成する必要があります。'
      },
      color: 'rgb(54, 227, 206)'
    },
    event: {
      title: {
        ko: '이벤트',
        en: 'Event',
        ja: 'イベントページ'
      },
      description: {
        ko: '사용자들이 랜딩해서 흥미로운 정보들을 탐색하고, 추가 페이지 전환을 통해 서비스 이용을 지속할 수 있도록 해야 해요.',
        en: 'users should be able to explore engaging information and continue using the service through additional page transitions.',
        ja: 'ユーザーが興味深い情報を探索し、追加のページ遷移を通じてサービスを継続的に利用できるようにする必要があります。'
      },
      color: 'rgba(90, 231, 138, 1)'
    },
    detail: {
      title: {
        ko: '정보 상세',
        en: 'Detail',
        ja: '詳細ページ'
      },
      description: {
        ko: '자세한 정보를 포함하고 있기 때문에, 사용자들의 적극적인 탐색을 유도해야 해요.',
        en: 'detailed information is provided, so it should encourage active exploration by users.',
        ja: '詳細な情報が含まれているため、ユーザーの積極的な探索を促す必要があります。'
      },
      color: 'rgb(221, 166, 255)'
    },
    recruit: {
      title: {
        ko: '채용',
        en: 'Job search',
        ja: '採用ページ'
      },
      description: {
        ko: '사용자가 많은 정보들 중 원하는 목적지를 잘 찾을 수 있도록 설계해야 해요.',
        en: 'it should be designed to help users find their desired destination among a large amount of information.',
        ja: '多くの情報の中からユーザーが目的地をうまく見つけられるように設計する必要があります。'
      },
      color: 'rgb(162, 218, 235)'
    },
    list: {
      title: {
        ko: '정보 목록/분류',
        en: 'List',
        ja: 'リストページ'
      },
      description: {
        ko: '사용자가 많은 정보들 중 원하는 목적지를 잘 찾을 수 있도록 설계해야 해요.',
        en: 'it should be designed to help users find their desired destination among a large amount of information.',
        ja: '多くの情報の中からユーザーが目的地をうまく見つけられるように設計する必要があります。'
      },
      color: 'rgb(157, 173, 255)'
    },
    main: {
      title: {
        ko: '메인',
        en: 'Main',
        ja: 'トップページ'
      },
      description: {
        ko: '서비스를 대표할 수 있는 콘텐츠와 브랜딩이 잘 전달되고 내비게이션이 잘 활용되어 전환하는 것을 목표로 해야 해요.',
        en: 'the goal should be to effectively communicate key content and branding while utilizing navigation to lead users to conversion.',
        ja: 'サービスを代表するコンテンツとブランドをうまく伝え、ナビゲーションを活用してコンバージョンを目指す必要があります。'
      },
      color: 'rgb(103, 209, 255)'
    }
  },
  tertiary: {
    main: {
      title: {
        ko: '메인/브랜딩',
        en: 'Main',
        ja: 'トップ'
      },
      keyword: {
        ko: '',
        en: '',
        ja: ''
      },
      descriptions: {
        ko: [
          '충분한 체류시간 동안 콘텐츠와 브랜딩을 잘 전달받았는지 확인해보세요.',
          '마우스오버와 스크롤 탐색이 높고 활발하게 나타나면서 메인의 주요 콘텐츠와 탐색 메뉴를 잘 활용했는지 검토해보세요.',
          '주요 콘텐츠로 잘 전환했는지 검토해보세요.'
        ],
        en: [
          'Check whether the content and branding are well delivered during sufficient stay time.',
          "Make sure that users' hover and scroll navigation is high and active, and that the main content and navigation menu are well utilized.",
          'Check whether the main content link has been successfully converted.'
        ],
        ja: [
          'カスタマーの滞在時間内で、コンテンツとブランディングが適切に配信されているかどうかを確認してください。',
          'カスタマーのマウスの動きや、スクロールなど、主要コンテンツとナビゲーションメニュー機能をカスタマーが活用しているかを、確認してください。',
          '主要コンテンツへコンバージョンしているのか、チェックしてみましょう。'
        ]
      }
    },
    list: {
      title: {
        ko: '목록',
        en: 'List',
        ja: 'リスト'
      },
      keyword: {
        ko: '',
        en: '',
        ja: ''
      },
      descriptions: {
        ko: [
          '상세 페이지로 잘 전환했는지 확인해보세요.',
          '짧은 체류시간으로 전환 결정을 빨리 내렸는지, 아니면 여러 콘텐츠를 다양하게 탐색하고 고민하면서 오래 체류하다 전환 결정을 내렸을 지 확인해보세요.'
        ],
        en: [
          'Check whether it has been converted to the details page.',
          'Check to see if the conversion decision was made quickly with a short stay, or if the conversion decision was made after a long stay while exploring and considering various contents.'
        ],
        ja: [
          '詳細ページへコンバージョンしているのか、チェックしてみましょう。',
          'カスタマーが、短い滞在期間で他のページにコンバージョンしたのか、もしくは色んなコンテンツの情報を収集して長い滞在時間をかけてコンバージョンしたのか確認してみましょう。'
        ]
      }
    },
    detail: {
      title: {
        ko: '정보 상세 안내',
        en: 'Detail',
        ja: '詳細'
      },
      keyword: {
        ko: '',
        en: '',
        ja: ''
      },
      descriptions: {
        ko: [
          '오랜 체류시간동안 체류하면서 콘텐츠를 잘 살펴봤을 지 확인해보세요.',
          '콘텐츠를 잘 살펴보기 위해 Mouseover가 충분히 분포되었는지 확인해보세요.',
          '콘텐츠를 끝까지 잘 살펴봤을 지 스크롤 도달율을 검토해보세요.'
        ],
        en: [
          'Check to see if you have looked at the content well during your long stay.',
          'Make sure Mouseover is sufficiently distributed to view your content.',
          'Review the scroll reach rate to see if the content was viewed to the end.'
        ],
        ja: [
          '長い滞在時間の間、カスタマーがコンテンツを消費しているのかチェックしてみましょう。',
          'コンテンツの詳細を確認するために、Mouseoverがされているか、チェックしてみましょう。',
          'コンテンツを最後まで、閲覧しているのかスクロール到達率を確認してみましょう。'
        ]
      }
    },
    cta: {
      title: {
        ko: 'CTA 유도',
        en: 'CTA',
        ja: 'CTA誘導'
      },
      keyword: {
        ko: '결제, 가입, 공유 등',
        en: 'Payment, subscription, sharing',
        ja: '決済、会員登録、シェアなど'
      },
      descriptions: {
        ko: [
          '중요한 CTA 링크가 위치한 곳에 사용자가 주목하는지 Attention을 살펴보세요.',
          '중요한 CTA 링크로 잘 전환하고 있는지 검토해보세요.'
        ],
        en: [
          'Look at Attention to see if users are paying attention to where your important CTA links are located.',
          "Review whether you're converting well to important call-to-action links."
        ],
        ja: [
          '重要なCTAリンクが配置されている場所に、ユーザーが注目しているのか、Attentionを、チェックしてみましょう。',
          '重要なCTAリンクへコンバージョンできているかチェックしてみましょう。'
        ]
      }
    },
    form: {
      title: {
        ko: '사용자입력',
        en: 'Form',
        ja: '入力フォーム'
      },
      keyword: {
        ko: '결제/주문 정보입력, 상품가입단계, 예약과정',
        en: 'Payment/Order Information Entry, Product Subscription Stage, Reservation Process',
        ja: '決済/注文、情報入力、商品購入、サービス予約'
      },
      descriptions: {
        ko: [
          '입력 서식이 잘 활용되고 있을 지, 각 서식들의 클릭과 Mouseover가 충분한 지 검토해보세요.',
          '특정 서식 활용에 어려움이 발생할 수 있으니, Attention이 불필요하게 높은 구간이 있는지 검토해보세요.'
        ],
        en: [
          'Check whether the input form is being used well and whether clicks and mouseovers for each form are sufficient.',
          'Difficulties may arise in using certain forms, so review whether there are sections where Attention is unnecessarily high.'
        ],
        ja: [
          '入力フォームが有効活用されているのか、入力フォームのクリックとMouseoverをチェックしてみましょう。',
          '入力フォームによっては、入力が難しい場合もありますので、Attentionが必要以上に高い箇所はないか、チェックしてみましょう。'
        ]
      }
    },
    info: {
      title: {
        ko: '정보 확인',
        en: 'Info',
        ja: '情報'
      },
      keyword: {
        ko: '내정보, 주문확인',
        en: 'My information, order confirmation',
        ja: 'マイページ、注文内容の確認'
      },
      descriptions: {
        ko: [
          '중요한 콘텐츠가 많은 사용자들에게 노출될 수 있을 지, 스크롤 도달율과 Attention을 살펴보세요.'
        ],
        en: [
          'Check scroll reach and attention to see if important content can be exposed to many users.'
        ],
        ja: [
          '重要なコンテンツが、多くのカスタマーに露出されているのか、スクロール到達率とAttentionをチェックしてみましょう。'
        ]
      }
    },
    etc: {
      title: {
        ko: '미분류',
        en: 'Still in progress',
        ja: '分類進行中'
      },
      keyword: {
        ko: '',
        en: '',
        ja: ''
      },
      descriptions: {
        ko: [],
        en: [],
        ja: []
      }
    },
    test: {
      title: {
        ko: '테스트',
        en: '',
        ja: ''
      },
      keyword: {
        ko: '',
        en: '',
        ja: ''
      },
      descriptions: {
        ko: [],
        en: [],
        ja: []
      }
    }
  }
}

export const HTTP_STATUS = {
  unauthorized: 401,
  forbidden: 403,
  unprocessableEntity: 422
}

export const BEUSABLE_TOKEN_COOKIE = '_beu_a_t_'

export const MONTHS = [
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'May',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec'
]

export const REPORT_META = {
  dashboard: {
    logoText: 'AI Customed Dashboard',
    useIframe: true,
    useChat: true,
    chatCategory: 'dashboardChat',
    serviceType: 'ba',
    iframeUrl: `${BEUSABLE_BASE_URL}/ai/journeymap/get_ai_dashboard/`
  },
  dashboardHell: {
    logoText: 'AI Customed Dashboard',
    useIframe: true,
    useChat: true,
    chatCategory: 'dashboardChat',
    serviceType: 'ba',
    iframeUrl: `${BEUSABLE_BASE_URL}/ai/journeymap/get_ai_dashboard/`
  },
  dashboardGa: {
    logoText: 'AI Customed Dashboard',
    useIframe: true,
    useChat: true,
    chatCategory: 'dashboardChat',
    serviceType: 'ba',
    iframeUrl: `${BEUSABLE_BASE_URL}/ai/journeymap/get_ai_dashboard/`
  },
  scroll: {
    useIframe: true,
    useChat: true,
    chatCategory: 'scrollChat',
    serviceType: 'beusable',
    iframeUrl: `${HUB_BASE_URL}/v1/heatmap/ai/report_html/`
  },
  schemaTag: {
    logoText: 'Schema Tag Report',
    useIframe: true,
    useChat: true,
    chatCategory: 'schemaChat',
    serviceType: 'geo',
    iframeUrl: `${HUB_BASE_URL}/v1/geo/schema/report_html/`
  },
  whitePaper: {
    useIframe: true,
    useChat: true,
    chatCategory: 'whitePaper',
    hideHeader: true,
    hideBanner: true,
    hideVersion: true,
    serviceType: 'geo',
    iframeUrl: `${HUB_BASE_URL}/v1/geo/schema/report_html/`
  },
  cxTrends: {
    useIframe: true,
    useChat: true,
    chatCategory: 'cxTrends',
    hideHeader: true,
    hideBanner: true,
    hideVersion: true,
    serviceType: 'geo',
    iframeUrl: `${HUB_BASE_URL}/v1/geo/schema/report_html/`
  }
}
