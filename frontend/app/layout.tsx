import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <header>My ToDo App</header>
          {children}
        </div>
      </body>
    </html>
  );
}
