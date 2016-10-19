--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: addrs; Type: TABLE; Schema: public; Owner: vagrant; Tablespace: 
--

CREATE TABLE addrs (
    addr_id integer NOT NULL,
    lat real NOT NULL,
    lng real NOT NULL
);


ALTER TABLE public.addrs OWNER TO vagrant;

--
-- Name: addrs_addr_id_seq; Type: SEQUENCE; Schema: public; Owner: vagrant
--

CREATE SEQUENCE addrs_addr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.addrs_addr_id_seq OWNER TO vagrant;

--
-- Name: addrs_addr_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vagrant
--

ALTER SEQUENCE addrs_addr_id_seq OWNED BY addrs.addr_id;


--
-- Name: labels; Type: TABLE; Schema: public; Owner: vagrant; Tablespace: 
--

CREATE TABLE labels (
    label_id integer NOT NULL,
    addr_id integer NOT NULL,
    user_id integer NOT NULL,
    label character varying(128) NOT NULL
);


ALTER TABLE public.labels OWNER TO vagrant;

--
-- Name: labels_label_id_seq; Type: SEQUENCE; Schema: public; Owner: vagrant
--

CREATE SEQUENCE labels_label_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.labels_label_id_seq OWNER TO vagrant;

--
-- Name: labels_label_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vagrant
--

ALTER SEQUENCE labels_label_id_seq OWNED BY labels.label_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: vagrant; Tablespace: 
--

CREATE TABLE users (
    user_id integer NOT NULL,
    email character varying(64) NOT NULL,
    password character varying(64) NOT NULL,
    fname character varying(64),
    lname character varying(64),
    celsius boolean,
    sensitivity integer
);


ALTER TABLE public.users OWNER TO vagrant;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: vagrant
--

CREATE SEQUENCE users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_user_id_seq OWNER TO vagrant;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vagrant
--

ALTER SEQUENCE users_user_id_seq OWNED BY users.user_id;


--
-- Name: addr_id; Type: DEFAULT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY addrs ALTER COLUMN addr_id SET DEFAULT nextval('addrs_addr_id_seq'::regclass);


--
-- Name: label_id; Type: DEFAULT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY labels ALTER COLUMN label_id SET DEFAULT nextval('labels_label_id_seq'::regclass);


--
-- Name: user_id; Type: DEFAULT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY users ALTER COLUMN user_id SET DEFAULT nextval('users_user_id_seq'::regclass);


--
-- Data for Name: addrs; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY addrs (addr_id, lat, lng) FROM stdin;
\.


--
-- Name: addrs_addr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vagrant
--

SELECT pg_catalog.setval('addrs_addr_id_seq', 1, false);


--
-- Data for Name: labels; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY labels (label_id, addr_id, user_id, label) FROM stdin;
\.


--
-- Name: labels_label_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vagrant
--

SELECT pg_catalog.setval('labels_label_id_seq', 1, false);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY users (user_id, email, password, fname, lname, celsius, sensitivity) FROM stdin;
1	rachel@roadcast.com	4690694929657687455	Rachel		f	1
\.


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vagrant
--

SELECT pg_catalog.setval('users_user_id_seq', 1, true);


--
-- Name: addrs_pkey; Type: CONSTRAINT; Schema: public; Owner: vagrant; Tablespace: 
--

ALTER TABLE ONLY addrs
    ADD CONSTRAINT addrs_pkey PRIMARY KEY (addr_id);


--
-- Name: labels_pkey; Type: CONSTRAINT; Schema: public; Owner: vagrant; Tablespace: 
--

ALTER TABLE ONLY labels
    ADD CONSTRAINT labels_pkey PRIMARY KEY (label_id);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: vagrant; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: labels_addr_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY labels
    ADD CONSTRAINT labels_addr_id_fkey FOREIGN KEY (addr_id) REFERENCES addrs(addr_id);


--
-- Name: labels_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY labels
    ADD CONSTRAINT labels_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

