//
//  PostStampedByView.h
//  Stamped
//
//  Created by Devin Doty on 6/17/12.
//
//

#import <UIKit/UIKit.h>
#import "STStampedBy.h"

@protocol PostStampedByViewDelegate;
@interface PostStampedByView : UIView {
    UIView *_contentView;
    NSArray *_views;
    UIButton *_button;
}

- (id)initWithFrame:(CGRect)frame entityIdentifier:(NSString*)entityIdentifier;
- (id)initWithFrame:(CGRect)frame stampedBy:(id<STStampedBy>)stampedBy;

@property(nonatomic,assign) id <PostStampedByViewDelegate> delegate;
@property(nonatomic,retain) id <STStampedBy> stampedBy;
@property(nonatomic,retain,readonly) UILabel *titleLabel;

@end
@protocol PostStampedByViewDelegate
- (void)postStampedByView:(PostStampedByView*)view selectedPreview:(id<STStampPreview>)item;
- (void)postStampedByView:(PostStampedByView*)view selectedAll:(id)sender;
@end