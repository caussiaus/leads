-- db/seed.sql
INSERT INTO organizations(name)
  VALUES
    ('Concordia University') ON CONFLICT DO NOTHING,
    ('University of Montreal') ON CONFLICT DO NOTHING;
