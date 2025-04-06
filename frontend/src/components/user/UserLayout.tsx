import { Outlet } from "react-router-dom";
import UserHeader from "./UserHeader";
import UserFooter from "./UserFooter";


function UserLayout() {
    return (
        <>
            <header>
                <UserHeader />
            </header>
            <div className="mt-12" style={{ minHeight: "60vh" }}>
                <Outlet />
            </div>
            <footer className="mt-14">
                <UserFooter />
            </footer>
        </>
    );
}

export default UserLayout;
