import { Outlet } from "react-router-dom";
import Header from "./Header";
import Footer from "./Footer";

interface Props {
    setTheme: React.Dispatch<React.SetStateAction<string>>;
}

function Layout({ setTheme }: Props) {
    return (
        <>
            <header className="mt-6">
                <Header setTheme={setTheme} />
            </header>
            <div style={{ minHeight: "60vh" }}>
                <Outlet />
            </div>
            <footer className="mt-6">
                <Footer />
            </footer>
        </>
    );
}

export default Layout;
