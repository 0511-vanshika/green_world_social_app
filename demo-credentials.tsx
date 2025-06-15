const demoAccounts = [
  { email: "test@example.com", password: "test", name: "Test User" },
  { email: "jane.doe@example.com", password: "password", name: "Jane Doe (Plant Lover)" },
  { email: "john.smith@example.com", password: "garden123", name: "John Smith (Garden Guru)" },
  { email: "sarah.green@example.com", password: "plants456", name: "Sarah Green (Green Thumb)" },
]

const DemoCredentials = () => {
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-muted-foreground">Demo Accounts:</p>
      {demoAccounts.map((account, index) => (
        <div key={index} className="text-xs text-muted-foreground bg-muted/50 p-2 rounded">
          <div className="font-medium">{account.name}</div>
          <div>Email: {account.email}</div>
          <div>Password: {account.password}</div>
        </div>
      ))}
    </div>
  )
}

export default DemoCredentials
