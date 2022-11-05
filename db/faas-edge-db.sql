CREATE TABLE public.smart_home
(
    id serial NOT NULL,
    "time" timestamp without time zone,
    use double precision,
    gen double precision,
    dw double precision,
    fu double precision,
    fu2 double precision,
    ho double precision,
    fridge double precision,
    wc double precision,
    PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.smart_home
    OWNER to postgres;