//
//  STTextCalloutView.h
//  Stamped
//
//  Created by Devin Doty on 6/6/12.
//
//

#import <UIKit/UIKit.h>
#import "STCalloutView.h"

@interface STTextCalloutView : STCalloutView {
    CATextLayer *_textLayer;
}
- (void)setTitle:(NSString*)title boldText:(NSString*)boldText;
@end
