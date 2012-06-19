//
//  STCreateCommentView.h
//  Stamped
//
//  Created by Devin Doty on 6/18/12.
//
//

#import <UIKit/UIKit.h>

@protocol STCreateCommentViewDelegate;
@interface STCreateCommentView : UIView {
    
    UIImageView *_textBackground;
    UITextView *_textView;
    UILabel *_placeholder;
    UIButton *_keyboardButton;
    BOOL _visible;
    BOOL _loading;
    
    NSString *_textStore;
    
    UIView *_backgroundView;
    UIActivityIndicatorView *_activityView;

}

@property(nonatomic,assign) id <STCreateCommentViewDelegate> delegate;
@property(nonatomic,retain) NSString *identifier;

- (NSString*)text;
- (void)setText:(NSString*)text;
- (void)showAnimated:(BOOL)animated;
- (void)killKeyboard;

- (void)keyboardWillShow:(NSDictionary*)userInfo;
- (void)keyboardWillHide:(NSDictionary*)userInfo;

@end
@protocol STCreateCommentViewDelegate
- (void)stCreateCommentView:(STCreateCommentView*)view addedComment:(id<STComment>)comment;
- (void)stCreateCommentViewWillBeginEditing:(STCreateCommentView*)view;
- (void)stCreateCommentViewWillEndEditing:(STCreateCommentView*)view;
@end