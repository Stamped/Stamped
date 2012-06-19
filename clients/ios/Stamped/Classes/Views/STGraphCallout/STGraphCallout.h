//
//  STGraphCallout.h
//  Stamped
//
//  Created by Devin Doty on 6/17/12.
//
//

#import <UIKit/UIKit.h>
#import "STCalloutView.h"

@interface STGraphCallout : STCalloutView {
    UIButton *_disclosureButton;
}
@property(nonatomic,assign) id delegate;
@property(nonatomic,copy) NSString *category;
- (void)setTitle:(NSString*)title boldText:(NSString*)boldText;
@end