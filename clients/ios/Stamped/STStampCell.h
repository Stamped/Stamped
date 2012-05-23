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

@class STBlockUIView, STPreviewsView;
@interface STStampCell : UITableViewCell {
    STBlockUIView *_headerView;
    STBlockUIView *_commentView;
    STPreviewsView *_statsView;
    UIImageView *_userImageView;
    UILabel *_dateLabel;    
    UIImage *_stampImage;
    UIImage *_categoryImage;
    
    BOOL _hasMedia;
    
}
@property(nonatomic,readonly) NSString *username;
@property(nonatomic,readonly) NSString *subcategory;
@property(nonatomic,readonly) NSString *title;
@property(nonatomic,readonly) NSString *category;
@property(nonatomic,readonly) NSString *identifier;
@property(nonatomic,readonly) NSInteger commentCount;

- (void)setupWithStamp:(id<STStamp>)stamp;

+ (CGFloat)heightForStamp:(id<STStamp>)stamp;

+ (STCancellation*)prepareForStamp:(id<STStamp>)stamp withCallback:(void (^)(NSError* error, STCancellation* cancellation))block;

+ (NSString*)cellIdentifier;

@end
