import '../index.css';

export const metadata = {
  title: 'SentinelBrief — Resilient Autonomous Competitive Intelligence',
  description: 'A resilient multi-agent competitive intelligence briefing system powered by Nemotron-70B on Crusoe Cloud, managed by TrueFoundry AI Gateway, Upstash Redis, and Neon PostgreSQL.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🛡️</text></svg>" />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
