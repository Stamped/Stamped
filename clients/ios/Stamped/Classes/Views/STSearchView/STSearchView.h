//
//  STSearchView.h
//  Stamped
//
//  Created by Devin Doty on 5/17/12.
//
//

#import <UIKit/UIKit.h>
#import "STSearchField.h"

@protocol STSearchViewDelegate;
@interface STSearchView : UIView {
    UIButton *_cancelButton;
}

@property(nonatomic,assign) id <STSearchViewDelegate> delegate;
@property(nonatomic,retain) UITextField *textField;
@property(nonatomic,assign,getter = showingCancel) BOOL showCancelButton;

@end
@protocol STSearchViewDelegate
- (void)stSearchViewDidCancel:(STSearchView*)view;
@end