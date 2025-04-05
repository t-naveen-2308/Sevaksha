import { Outlet } from "react-router-dom";
import UserHeader from "./UserHeader";
import UserFooter from "./UserFooter";

interface Props {
    setTheme: React.Dispatch<React.SetStateAction<string>>;
}

function UserLayout({ setTheme }: Props) {
    return (
        <>
            <header>
                <UserHeader setTheme={setTheme} />
            </header>
            <div className="mt-24" style={{ minHeight: "60vh" }}>
                <Outlet />
            </div>
            <footer className="mt-14">
                <UserFooter />
            </footer>
        </>
    );
}

export default UserLayout;
