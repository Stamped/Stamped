//
//  STSearchView.h
//  Stamped
//
//  Created by Devin Doty on 5/17/12.
//
//

#import <UIKit/UIKit.h>
#import "STSearchField.h"

@interface STSearchView : UIView
@property(nonatomic,retain) UITextField *textField;
@property(nonatomic,assign,getter = showingCancel) BOOL showCancelButton;
@end
