import {
    createBrowserRouter,
    RouterProvider,
    Navigate
} from "react-router-dom";
import {
    Layout,
    Login,
    Sections,
    Section,
    Books,
    Book,
    ViewBook,
    Statistics,
    Account,
    AddOrEditUser,
    ChangePassword
} from "./components/common";
import { RedirectIfNotAuthenticated } from "./utils";
import { useSelector } from "react-redux";

interface Props {
    setTheme: React.Dispatch<React.SetStateAction<string>>;
}

function BrowserRouterProvider({ setTheme }: Props) {
    const user = useSelector((state: RootState) => state.user);
    const isAuthenticated = user!==null;

    const BrowserRouter = createBrowserRouter([
        {
            path: "/",
            element: <Layout to="" setTheme={setTheme} />,
            children: [
                {
                    path: "sections",
                    element: <Sections to="" />
                },
                {
                    path: "section/:sectionSlug",
                    element: <Section to="" />
                },
                {
                    path: "books",
                    element: <Books to="" />
                },
                {
                    path: "section/:sectionSlug/book/:bookSlug",
                    element: <Book to="" />
                },
                {
                    path: "register",
                    element: <AddOrEditUser to="add" to1="user" />
                },
                {
                    path: "login",
                    element: <Login />
                },
                {
                    path: "",
                    element: <Navigate to="sections" />
                }
            ]
        }
    ]);

    return (
        <>
            <RouterProvider router={BrowserRouter} />
        </>
    );
}

export default BrowserRouterProvider;
