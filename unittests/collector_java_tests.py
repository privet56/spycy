import sys, os
import unittest

sys.path.append(os.getcwd()+'/../lib')

from collector_java import Collector_java

class KnownValues(unittest.TestCase):

    def test_replace_literals(self):
        java_str = '''
        import java.lang.string;

        //this is a java class

        class AJavaClass {
            /* the constructor */
            public AJavaClass()
            {

            }
            /*
            * this is a java function
            */
            public myFunction1(String str, int i) {
                String aString = "a string";
                char c = 'c';
                int i = 1;
                float f = 0.001;
            }
            /*
            * this is another java function
            */
            public myFunction2(String str, int i) {
                String aString = "a string";
                char c = 'c';
                int i = 1;
                float f = 0.001;
            }
        }
        '''

        java_str_without_mulitline_comment = Collector_java.replace_literals(java_str)

        assert len(java_str) > (len(java_str_without_mulitline_comment) + 9)
        assert len(java_str_without_mulitline_comment) > 9


if __name__ == '__main__':
    unittest.main()
