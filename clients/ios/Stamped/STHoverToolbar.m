//
//  STHoverToolbar.m
//  Stamped
//
//  Created by Landon Judkins on 6/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STHoverToolbar.h"
#import "STLikeButton.h"
#import "STStampButton.h"
#import "STShareButton.h"
#import "STTodoButton.h"
#import "STCommentButton.h"

@implementation STHoverToolbar

@synthesize target = _target;
@synthesize commentAction = _commentAction;
@synthesize shareAction = _shareAction;

- (id)initWithStamp:(id<STStamp>)stamp andEntityDetail:(id<STEntityDetail>)entityDetail {
    UIImage *image = [UIImage imageNamed:@"st_detail_action_bg"];
    
    CGFloat height = image.size.height;
    CGFloat buttonPadding = 5;
    CGFloat buttonSpacing = 10;
    CGFloat buttonWidth = 50;
    NSInteger buttonCount = stamp ? 5 : 2;
    CGRect frame = CGRectMake(0, 0, buttonCount * buttonWidth + (buttonCount - 1) * buttonSpacing + 2 * buttonPadding, height);
    self = [super initWithFrame:frame];
    if (self) {
        UIImageView *background = [[[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]] autorelease];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        background.frame = self.frame;
        [self addSubview:background];
        
        NSArray* buttons;
        if (stamp) {
            __block STHoverToolbar* weakSelf = self;
            STCommentButton* commentButton = [[[STCommentButton alloc] initWithCallback:^{
                if (weakSelf.target && weakSelf.commentAction) {
                    [weakSelf.target performSelector:weakSelf.commentAction];
                }
            }] autorelease];
            
            buttons = [[NSArray arrayWithObjects:
                        [[[STLikeButton alloc] initWithStamp:stamp] autorelease],
                        commentButton,
                        [[[STStampButton alloc] initWithStamp:stamp] autorelease],
                        [[[STTodoButton alloc] initWithStamp:stamp] autorelease],
                        [[[STShareButton alloc] initWithCallback:^{
                if (weakSelf.target && weakSelf.shareAction) {
                    [weakSelf.target performSelector:weakSelf.shareAction];
                }
            }] autorelease], nil] retain];
        }
        else {
            buttons = [[NSArray arrayWithObjects:
                        [[[STStampButton alloc] initWithEntity:entityDetail] autorelease],
                        [[[STTodoButton alloc] initWithEntityID:entityDetail.entityID] autorelease],
                        nil] retain];
        }
        for (NSInteger i = 0; i < buttons.count; i++) {
            UIView* button = [buttons objectAtIndex:i];
            [Util reframeView:button withDeltas:CGRectMake(buttonPadding + i * (buttonWidth + buttonSpacing), -6.5, 0, 0)];
            [self addSubview:button];
        }
    }
    return self;
}

- (id)initWithStamp:(id<STStamp>)stamp {
    return [self initWithStamp:stamp andEntityDetail:nil];
}

- (id)initWithEntity:(id<STEntityDetail>)entityDetail {
    return [self initWithStamp:nil andEntityDetail:entityDetail];
}

- (void)reloadStampedData {
    for (id view in self.subviews) {
        if ([view respondsToSelector:@selector(reloadStampedData)]) {
            [view reloadStampedData]; 
        }
    }
}

- (void)positionInParent {
    CGRect bounds = CGRectMake(0, self.superview.frame.size.height - self.frame.size.height - 5, self.superview.frame.size.width, self.frame.size.height);
    self.frame = [Util centeredAndBounded:self.frame.size inFrame:bounds];
}

@end
