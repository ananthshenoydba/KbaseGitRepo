SET TERM ON;
SET SERVEROUTPUT ON;
BEGIN
FOR i IN (
SELECT 'ALTER TABLE TFS.'||a.table_name || ' ENABLE NOVALIDATE CONSTRAINT ' || a.constraint_name statement FROM
(
select distinct b.constraint_name, b.table_name
  from dba_constraints a, dba_constraints b, dba_cons_columns c
 where a.owner=b.r_owner
   and b.owner=c.owner
   and b.table_name=c.table_name
   and b.constraint_name=c.constraint_name
   and a.constraint_name=b.r_constraint_name
   and b.constraint_type='R'
   and a.owner='TFS'
 ) a
)
    LOOP
      BEGIN
        EXECUTE IMMEDIATE i.statement;
        DBMS_OUTPUT.PUT_LINE('Constraint Enabled ==> '||i.statement);
      EXCEPTION
        WHEN OTHERS THEN
          DBMS_OUTPUT.PUT_LINE('Constraint not Enabled ... '||i.statement||SQLERRM);
      END;
    END LOOP;
END;
/
