// TODO: Wire to Firebase Auth — admin account stays logged in permanently, no session timeout

export const mockAuth = {
  isLoggedIn: true,
  user: {
    name: "Admin",
    email: "admin@curryinbarrie.ca",
  },
};
