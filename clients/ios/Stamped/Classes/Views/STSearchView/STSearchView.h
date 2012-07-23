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
    UIActivityIndicatorView *_activityView;
}

@property(nonatomic,assign) id <STSearchViewDelegate> delegate;
@property(nonatomic,assign,getter = showingCancel) BOOL showCancelButton;
@property(nonatomic,assign,getter = isLoading) BOOL loading;

- (void)cancelSearch;
- (void)setPlaceholderTitle:(NSString*)title;
- (void)setText:(NSString*)text;
- (NSString*)text;
- (void)resignKeyboard;

@end
@protocol STSearchViewDelegate
- (void)stSearchViewDidCancel:(STSearchView*)view;
- (void)stSearchViewDidBeginSearching:(STSearchView*)view;
- (void)stSearchViewDidEndSearching:(STSearchView*)view;
@optional
- (void)stSearchViewHitSearch:(STSearchView*)view withText:(NSString*)text;
- (void)stSearchView:(STSearchView*)view textDidChange:(NSString*)text;
@end
