import { Navigate } from "react-router-dom";

interface Props {
    isAuthenticated: boolean;
    component: JSX.Element;
}

function RedirectIfNotAuthenticated({
    isAuthenticated,
    component
}: Props) {
    console.log(isAuthenticated);
    return (
        <>
            {true ? (
                component
            ) : (
                <Navigate to="/user/login" />
            )}
        </>
    );
}

export default RedirectIfNotAuthenticated;
