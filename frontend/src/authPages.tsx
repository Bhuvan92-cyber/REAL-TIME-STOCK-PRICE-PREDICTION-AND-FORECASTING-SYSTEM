import { FormEvent, useState, type ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "./auth";
import { supabase } from "./supabase";

function AuthForm({ mode }: { mode: "login" | "register" | "forgot" }) {
  const { signIn, signUp, resetPassword, configured } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    if (!email.includes("@")) return setError("Enter a valid email address.");
    if (mode !== "forgot" && password.length < 8) return setError("Password must contain at least 8 characters.");
    setBusy(true);
    try {
      if (mode === "login") {
        await signIn(email, password);
        const target = new URLSearchParams(location.search).get("next") || "/";
        navigate(target);
      } else if (mode === "register") {
        await signUp(email, password, displayName);
        setMessage("Account created. Check your email if confirmation is enabled.");
      } else {
        await resetPassword(email);
        setMessage("If the account exists, a password-reset email has been sent.");
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Authentication failed.");
    } finally {
      setBusy(false);
    }
  }

  if (!configured) return <AuthLayout><p className="error">Authentication is not configured. Add the public Supabase environment variables.</p></AuthLayout>;
  const title = mode === "login" ? "Welcome back" : mode === "register" ? "Create your account" : "Reset your password";
  return <AuthLayout><form className="card auth-card" onSubmit={submit}>
    <p className="eyebrow">ACCOUNT</p><h2>{title}</h2>
    {mode === "register" && <input required placeholder="Display name" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />}
    <input required type="email" placeholder="Email address" value={email} onChange={(e) => setEmail(e.target.value)} />
    {mode !== "forgot" && <input required type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />}
    {error && <p className="error">{error}</p>}{message && <p className="success">{message}</p>}
    <button disabled={busy}>{busy ? "Working…" : title}</button>
    <p className="auth-links">{mode !== "login" && <Link to="/login">Log in</Link>} {mode === "login" && <Link to="/register">Create account</Link>} {mode === "login" && <Link to="/forgot-password">Forgot password?</Link>}</p>
  </form></AuthLayout>;
}

export function AuthLayout({ children }: { children: ReactNode }) {
  return <main className="auth-shell"><Link to="/" className="brand">Stock Analytics</Link>{children}</main>;
}
export const Login = () => <AuthForm mode="login" />;
export const Register = () => <AuthForm mode="register" />;
export const ForgotPassword = () => <AuthForm mode="forgot" />;
export function ResetPassword() {
  const { configured } = useAuth();
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  if (!configured) return <AuthLayout><p className="error">Authentication is not configured.</p></AuthLayout>;
  return <AuthLayout><form className="card auth-card" onSubmit={async (event) => {
    event.preventDefault();
    if (password.length < 8) return setMessage("Password must contain at least 8 characters.");
    const { error } = await supabase!.auth.updateUser({ password });
    setMessage(error?.message ?? "Password updated. You can now log in.");
  }}><h2>Choose a new password</h2><input required type="password" placeholder="New password" value={password} onChange={(e) => setPassword(e.target.value)} /><button>Update password</button>{message && <p>{message}</p>}</form></AuthLayout>;
}
