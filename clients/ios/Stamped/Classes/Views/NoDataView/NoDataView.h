//
//  NoDataView.h
//  Fav.TV
//
//  Created by Devin Doty on 2/9/11.
//  Copyright 2011 enormego. All rights reserved.
//


#import <UIKit/UIKit.h>

@class NoDataImageView;
@interface NoDataView : UIView {
	
	UIImageView *_imageView;
	UILabel *_textLabel;
	UILabel *_detailedTextLabel;
    CATextLayer *_detailedTextLayer;
}

@property(nonatomic,strong) UIImageView *imageView;
@property(nonatomic,strong) UILabel *textLabel;
@property(nonatomic,strong) UILabel *detailTextLabel;

- (void)setTitle:(NSString *)title detailedTitle:(id)detailTitle imageName:(NSString*)imageName;

@end
