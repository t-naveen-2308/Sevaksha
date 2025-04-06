import { Outlet } from "react-router-dom";
import Header from "./Header";
import Footer from "./Footer";

function Layout() {
    return (
        <>
            <header className="mt-6">
                <Header />
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
