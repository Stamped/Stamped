//
//  STStampCell.h
//  Stamped
//
//  Created by Landon Judkins on 4/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STStamp.h"
#import "STCancellation.h"

@protocol STStampCellDelegate;
@class STBlockUIView, STPreviewsView, STDetailTextCallout, STAvatarView;
@interface STStampCell : UITableViewCell {
    STBlockUIView *_headerView;
    STBlockUIView *_commentView;
    STPreviewsView *_statsView;
    CAShapeLayer *_statsDots;
    UIImageView *_footerImageView;
    UILabel *_dateLabel;    
    UIImage *_categoryImage;
    
    BOOL _hasMedia;
    STDetailTextCallout *_callout;
    STCancellation *_cancellation;
    
    UIColor *_primaryColor;
    UIColor *_secondarayColor;
    
    float r, g, b, r1, g1, b1;
    
}
@property(nonatomic,readonly) NSString *username;
@property(nonatomic,readonly) NSString *subcategory;
@property(nonatomic,readonly) NSString *title;
@property(nonatomic,readonly) NSString *category;
@property(nonatomic,readonly) NSString *identifier;
@property(nonatomic,readonly) NSInteger commentCount;

@property(nonatomic,assign) id <STStampCellDelegate> delegate;

- (void)setupWithStamp:(id<STStamp>)stamp;

+ (CGFloat)heightForStamp:(id<STStamp>)stamp;

+ (STCancellation*)prepareForStamp:(id<STStamp>)stamp withCallback:(void (^)(NSError* error, STCancellation* cancellation))block;

+ (NSString*)cellIdentifier;

@end

@protocol STStampCellDelegate
- (void)stStampCellAvatarTapped:(STStampCell*)cell;
@end