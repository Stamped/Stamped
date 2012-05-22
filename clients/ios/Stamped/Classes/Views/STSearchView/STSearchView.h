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
    UIImageView *_topLeftCorner;
    UIImageView *_topRightCorner;
    UITapGestureRecognizer *_tap;
    UITextField *_textField;
}

@property(nonatomic,assign) id <STSearchViewDelegate> delegate;
@property(nonatomic,assign,getter = showingCancel) BOOL showCancelButton;

- (void)cancelSearch;
- (void)setPlaceholderTitle:(NSString*)title;

@end
@protocol STSearchViewDelegate
- (void)stSearchViewDidCancel:(STSearchView*)view;
- (void)stSearchViewDidBeginSearching:(STSearchView*)view;
- (void)stSearchViewDidEndSearching:(STSearchView*)view;
- (void)stSearchView:(STSearchView*)view textDidChange:(NSString*)text;
@end
