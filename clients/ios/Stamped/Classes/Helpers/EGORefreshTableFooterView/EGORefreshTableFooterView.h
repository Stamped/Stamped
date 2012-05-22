//
//  EGORefreshTableFooterView.h
//  Fav.TV
//
//  Created by Devin Doty on 2/23/11.
//  Copyright 2011 enormego. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface EGORefreshTableFooterView : UIView {
	
	UIActivityIndicatorView *_activity;
	UIImageView *_shadowView;
	UILabel *_endLabel;
    
    
    UIImageView *_footerImageView;

}

- (void)showShadow:(BOOL)show;
- (void)setLoading:(BOOL)loading;

@end
